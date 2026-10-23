<?php
// Request form handler for the static export (manage.py export_static): the forms post to
// /zayavka/, .htaccess hands the POST here. The lead is checked like the Django form does,
// appended to ~/temir-gidro/leads.csv (outside the web root) and mailed. Mail settings live in
// ~/temir-gidro/lead-config.php, also outside the web root (see deploy/static/README.md):
//   <?php return ['to' => 'seo@temir.ru', 'smtp_user' => 'seo@temir.ru', 'smtp_password' => '…'];
// With an SMTP password the mail goes through smtp.mail.ru, otherwise through PHP mail().
// Written for PHP 7.0+.

$home = dirname(dirname(__DIR__));  // public_html/zayavka/send.php → the site's folder
$config = array(
    'to' => 'seo@temir.ru',
    'smtp_host' => 'ssl://smtp.mail.ru',
    'smtp_port' => 465,
    'smtp_user' => 'seo@temir.ru',
    'smtp_password' => '',
    'site' => 'temir-gidro.ru',
);
if (is_file($home . '/lead-config.php')) {
    $config = array_merge($config, (array) include $home . '/lead-config.php');
}

$wantsJson = strpos(isset($_SERVER['HTTP_ACCEPT']) ? $_SERVER['HTTP_ACCEPT'] : '', 'application/json') !== false;

function answer($ok, $errors, $wantsJson) {
    if ($wantsJson) {
        header('Content-Type: application/json; charset=utf-8');
        if (!$ok) { http_response_code(400); }
        echo json_encode($ok ? array('ok' => true) : array('ok' => false, 'errors' => $errors), JSON_UNESCAPED_UNICODE);
        exit;
    }
    if ($ok) {
        header('Location: /zayavka/spasibo/', true, 303);
        exit;
    }
    http_response_code(400);
    header('Content-Type: text/html; charset=utf-8');
    echo '<!doctype html><meta charset="utf-8"><title>Заявка не отправлена</title>';
    echo '<p style="font:16px/1.5 sans-serif;margin:3rem auto;max-width:36rem">';
    foreach ($errors as $list) { foreach ($list as $e) { echo htmlspecialchars($e['message']) . '<br>'; } }
    echo '<br><a href="javascript:history.back()">Вернуться к форме</a></p>';
    exit;
}

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    header('Location: /zayavka/', true, 302);
    exit;
}

function field($name, $max) {
    $v = isset($_POST[$name]) ? trim((string) $_POST[$name]) : '';
    return function_exists('mb_substr') ? mb_substr($v, 0, $max, 'UTF-8') : substr($v, 0, $max * 2);
}
$name = field('name', 100);
$phone = preg_replace('/[^\d+]/', '', field('phone', 32));
$email = field('email', 254);
$message = field('message', 2000);
$page = field('page', 500);
if (strpos($page, '/') !== 0 || strpos($page, '//') === 0) { $page = ''; }

$errors = array();
if ($name === '') { $errors['name'] = array(array('message' => 'Укажите, как к вам обращаться.')); }
$digits = ltrim($phone, '+');
if (!ctype_digit($digits) || strlen($digits) < 10 || strlen($digits) > 15) {
    $errors['phone'] = array(array('message' => 'Укажите номер телефона полностью, например +7 700 123-45-67.'));
}
if ($email !== '' && !filter_var($email, FILTER_VALIDATE_EMAIL)) {
    $errors['email'] = array(array('message' => 'Введите правильный адрес электронной почты.'));
}
if (empty($_POST['consent'])) {
    $errors['consent'] = array(array('message' => 'Без согласия мы не можем принять заявку.'));
}
if ($errors) { answer(false, $errors, $wantsJson); }

// Spam: the hidden field is filled or the text is full of links — answer "sent", send nothing.
$links = '/https?:\/\/|www\.|\[url|<a\s/i';
$spam = !empty($_POST['website']) || preg_match($links, $name) || preg_match_all($links, $message) > 1;

// At most 5 leads from one IP in 10 minutes.
$ip = isset($_SERVER['HTTP_X_FORWARDED_FOR']) ? trim(explode(',', $_SERVER['HTTP_X_FORWARDED_FOR'])[0]) : $_SERVER['REMOTE_ADDR'];
$stamp = sys_get_temp_dir() . '/temir-lead-' . md5($ip);
$recent = array_filter(is_file($stamp) ? explode("\n", (string) file_get_contents($stamp)) : array(), function ($t) {
    return $t !== '' && (int) $t > time() - 600;
});
if (count($recent) >= 5) {
    answer(false, array('__all__' => array(array('message' => 'Слишком много заявок подряд. Позвоните нам или попробуйте позже.'))), $wantsJson);
}
$recent[] = (string) time();
@file_put_contents($stamp, implode("\n", $recent));

$when = date('Y-m-d H:i:s');
$csv = fopen($home . '/leads.csv', 'a');
if ($csv) {
    fputcsv($csv, array($when, $spam ? 'spam' : 'new', $name, $phone, $email, $message, $page, $ip));
    fclose($csv);
}
if ($spam) { answer(true, array(), $wantsJson); }

$lines = array('Имя: ' . $name, 'Телефон: ' . $phone);
if ($email !== '') { $lines[] = 'Email: ' . $email; }
if ($message !== '') { $lines[] = ''; $lines[] = 'Комментарий:'; $lines[] = $message; $lines[] = ''; }
if ($page !== '') { $lines[] = 'Страница: https://' . $config['site'] . $page; }
$lines[] = 'Отправлено: ' . $when;
$body = implode("\r\n", $lines);
$subject = 'Заявка с сайта: ' . $name . ', ' . $phone;

function encode_header($s) { return '=?UTF-8?B?' . base64_encode($s) . '?='; }

function smtp_send($config, $subject, $body, $replyTo) {
    $fp = @stream_socket_client($config['smtp_host'] . ':' . $config['smtp_port'], $errno, $errstr, 15);
    if (!$fp) { return 'connect: ' . $errstr; }
    stream_set_timeout($fp, 15);
    $read = function () use ($fp) {
        $data = '';
        while (($line = fgets($fp, 1024)) !== false) {
            $data .= $line;
            if (strlen($line) < 4 || $line[3] === ' ') { break; }
        }
        return $data;
    };
    $cmd = function ($line, $expect) use ($fp, $read) {
        fwrite($fp, $line . "\r\n");
        $reply = $read();
        return strpos($reply, (string) $expect) === 0 ? '' : trim($line === '' ? $reply : explode(' ', $line)[0] . ': ' . $reply);
    };
    $read();
    $from = $config['smtp_user'];
    $headers = 'From: ' . encode_header('Сайт ' . $config['site']) . ' <' . $from . ">\r\n"
        . 'To: <' . $config['to'] . ">\r\n"
        . ($replyTo ? 'Reply-To: <' . $replyTo . ">\r\n" : '')
        . 'Subject: ' . encode_header($subject) . "\r\n"
        . 'Date: ' . date('r') . "\r\n"
        . "MIME-Version: 1.0\r\nContent-Type: text/plain; charset=UTF-8\r\nContent-Transfer-Encoding: base64\r\n";
    $steps = array(
        array('EHLO ' . $config['site'], 250),
        array('AUTH LOGIN', 334),
        array(base64_encode($from), 334),
        array(base64_encode($config['smtp_password']), 235),
        array('MAIL FROM:<' . $from . '>', 250),
        array('RCPT TO:<' . $config['to'] . '>', 250),
        array('DATA', 354),
        array($headers . "\r\n" . chunk_split(base64_encode($body)) . "\r\n.", 250),
    );
    foreach ($steps as $s) {
        $err = $cmd($s[0], $s[1]);
        if ($err !== '') { fclose($fp); return $err; }
    }
    $cmd('QUIT', 221);
    fclose($fp);
    return '';
}

$replyTo = $email !== '' ? $email : '';
if ($config['smtp_password'] !== '') {
    $error = smtp_send($config, $subject, $body, $replyTo);
} else {
    $headers = 'From: ' . encode_header('Сайт ' . $config['site']) . ' <noreply@' . $config['site'] . ">\r\n"
        . ($replyTo ? 'Reply-To: ' . $replyTo . "\r\n" : '')
        . "MIME-Version: 1.0\r\nContent-Type: text/plain; charset=UTF-8\r\nContent-Transfer-Encoding: base64";
    $error = mail($config['to'], encode_header($subject), chunk_split(base64_encode($body)), $headers) ? '' : 'mail() failed';
}
if ($error !== '') {
    // The lead is in leads.csv anyway; the visitor sees it as sent.
    error_log('temir-gidro lead mail: ' . $error);
}
answer(true, array(), $wantsJson);
