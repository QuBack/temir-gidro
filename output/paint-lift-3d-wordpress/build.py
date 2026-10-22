from pathlib import Path
from html import escape
from PIL import Image
import json
import re
import zipfile

ROOT = Path(__file__).resolve().parent
SOURCE = Path(r"C:\Users\user\.codex\attachments\4c3e38d1-c2a2-4224-a234-2769158d0546\Вставленный текст.txt")
BASE = "__TG_IMAGES_URL__"
IMAGES = ROOT / "images"
IMAGES.mkdir(parents=True, exist_ok=True)
items = [
    dict(id="general", file=r"C:\Users\user\AppData\Local\Temp\codex-clipboard-85972b41-ae49-4296-a6c7-449904b92bcb.png",
         name="podemnik-okrasochnoj-kamery-3d-obshchij-vid",
         alt="Красный подъемник для окрасочной камеры 3D с выдвижной кабиной и горизонтальными направляющими", label="Общий вид"),
    dict(id="side", file=r"C:\Users\user\AppData\Local\Temp\codex-clipboard-fe1c98bf-8693-46cc-904e-90417531af18.png",
         name="podemnik-okrasochnoj-kamery-3d-bokovoj-vid",
         alt="Подъемник 3D для окрасочной камеры сбоку: мачта, привод и выдвинутая рабочая кабина", label="Боковой ракурс"),
    dict(id="right", file=r"C:\Users\user\AppData\Local\Temp\codex-clipboard-dcd915db-2e83-4a1a-afe9-4b9c0d3fadab.png",
         name="podemnik-okrasochnoj-kamery-3d-pravyj-rakurs",
         alt="Подъемник для окрасочной камеры 3D в правом ракурсе с кабиной, направляющими и гидроцилиндром", label="Правый ракурс"),
    dict(id="tank", file=r"C:\Users\user\AppData\Local\Temp\codex-clipboard-a1681544-719c-4f20-9da9-0b886773ca5c.png",
         name="okraska-cisterny-podemnik-3d",
         alt="Маляр в кабине красного подъемника 3D окрашивает синюю цистерну в промышленной окрасочной камере", label="Окраска цистерны"),
]
manifest = []
for item in items:
    original = Image.open(item["file"])
    item["width"], item["height"] = original.size
    rgb = original.convert("RGB")
    widths = ([240] if item["id"] != "tank" else []) + [480, 800, 1200, item["width"]]
    item["variants"] = []
    for width in widths:
        height = round(item["height"] * width / item["width"])
        image = rgb.resize((width, height), Image.Resampling.LANCZOS) if width != item["width"] else rgb
        suffix = "" if width == item["width"] else f"-{width}"
        filename = f'{item["name"]}{suffix}.webp'
        metadata = {key: original.info[key] for key in ("xmp", "exif") if original.info.get(key)}
        image.save(IMAGES / filename, "WEBP", quality=86 if item["id"] == "tank" else 88, method=6, **metadata)
        variant = dict(file=filename, width=width, height=height, bytes=(IMAGES / filename).stat().st_size)
        item["variants"].append(variant)
        manifest.append(dict(source=item["id"], **variant))

def srcset(item):
    return ", ".join(f'{BASE}/{v["file"]} {v["width"]}w' for v in item["variants"] if v["width"] >= 480)

def url(item, width=1200):
    return f'{BASE}/{next(v["file"] for v in item["variants"] if v["width"] == width)}'

html = SOURCE.read_text(encoding="utf-8-sig")
style = re.search(r"<style>(.*?)</style>", html, re.S).group(1)
style = re.sub(r"\s*/\* Google Fonts \*/\s*@import[^;]+;", "", style)
style = style.replace(".tg-component", "#tg-paint-lift-3d")
style += """
    /* Show the complete images on desktop and mobile. */
    #tg-paint-lift-3d .tg-gallery-stage { background: #FFFFFF; }
    #tg-paint-lift-3d .tg-gallery-thumb img { pointer-events: none; }
    #tg-paint-lift-3d .tg-use-media { aspect-ratio: auto; background: #FFFFFF; }
    #tg-paint-lift-3d .tg-use-media img { height: auto; object-fit: contain; }
    #tg-paint-lift-3d .tg-use-case:hover .tg-use-media img { transform: none; }
    #tg-paint-lift-3d .tg-use-media figcaption {
      padding: 11px 14px; color: var(--tg-text-light); background: #F8FAFC;
      font-size: 12.5px; line-height: 1.5; border-top: 1px solid var(--tg-border);
    }
    #tg-paint-lift-3d .tg-use-copy a, #tg-paint-lift-3d .tg-desc-intro a {
      color: #A60000; text-decoration: underline; text-underline-offset: 3px;
    }
    @media (prefers-reduced-motion: reduce) {
      #tg-paint-lift-3d *, #tg-paint-lift-3d *::before, #tg-paint-lift-3d *::after {
        animation: none !important; transition: none !important;
      }
    }
"""
html = re.sub(r"<style>.*?</style>", lambda _: "<style>" + style + "\n  </style>", html, count=1, flags=re.S)
# Keep all content visible without JS or a scroll animation.
html = re.sub(r'\s+data-tg-reveal=""', "", html)
html = html.replace('aria-label="Галерея видов и схем подъемника 3D"', 'role="region" aria-roledescription="галерея" aria-label="Три ракурса подъемника для окрасочной камеры 3D"')
thumbs = []
for i, item in enumerate(items[:3]):
    thumb = next(v for v in item["variants"] if v["width"] == 240)
    thumbs.append(f"""
          <button class="tg-gallery-thumb{' active' if i == 0 else ''}" type="button"
            data-src="{url(item)}" data-srcset="{escape(srcset(item), quote=True)}"
            data-alt="{escape(item['alt'], quote=True)}"
            data-width="{item['width']}" data-height="{item['height']}"
            aria-label="Показать: {item['label'].lower()}" aria-pressed="{'true' if i == 0 else 'false'}">
            <img src="{BASE}/{thumb['file']}" alt="" width="{thumb['width']}" height="{thumb['height']}"
              loading="eager" decoding="async" aria-hidden="true">
          </button>""")
html = re.sub(r'(<div class="tg-gallery-thumbs"[^>]*>).*?(</div>)', lambda m: m[1] + "".join(thumbs) + "\n        " + m[2], html, count=1, flags=re.S)
general, side, right, tank = items
main = f"""<img class="tg-gallery-main" src="{url(general)}"
            srcset="{srcset(general)}"
            sizes="(max-width: 767px) calc(100vw - 146px), (max-width: 1024px) calc(100vw - 178px), 646px"
            alt="{general['alt']}" width="{general['width']}" height="{general['height']}"
            loading="eager" decoding="async" fetchpriority="high">"""
html = re.sub(r'<img class="tg-gallery-main"[^>]*>', lambda _: main, html, count=1)
html = html.replace('aria-live="polite"', 'aria-live="polite" aria-atomic="true"')
html = html.replace('<span class="tg-current">', '<span class="tg-current" aria-current="page">')
hero_desc = """<p class="tg-product-desc">Подъемники для окрасочных камер 3D от завода «ТЕМИР ГИДРО» перемещают рабочую кабину в трех направлениях: вверх и вниз, вдоль изделия и к его поверхности. Оператор выбирает положение для окраски цистерн, промышленных емкостей и крупных металлоконструкций. Рельсовая система и выдвижная кабина позволяют обслуживать протяженные поверхности с одного рабочего места.</p>"""
html = re.sub(r'<p class="tg-product-desc">.*?</p>', lambda _: hero_desc, html, count=1, flags=re.S)
html = html.replace("Применение подъемников для окрасочных камер 3D</h2>", "Применение подъемников 3D в окрасочной камере</h2>")
html = html.replace("Применение рельсового подъемника 3D с выдвижной кабиной при окраске транспорта, емкостей и металлоконструкций.", "Доступ к верхним и боковым участкам цистерн, резервуаров и других крупногабаритных изделий.")

description = f"""<div class="tg-desc-single-col">
      <div class="tg-desc-intro">
        <p><strong>Подъемник для окрасочной камеры серии 3D</strong> — рельсовая рабочая платформа с выдвижной кабиной для промышленных малярных участков. Продольное перемещение задает положение вдоль изделия, вертикальный подъем — высоту обслуживания, а выдвижение кабины — расстояние до поверхности. Рабочие диапазоны определяют по габаритам камеры и форме окрашиваемых деталей.</p>
        <p>Для цилиндрических емкостей при подборе учитывают диаметр, длину, расположение опор и выступающих элементов. Кабина должна подходить к рабочей зоне с учетом маршрута шлангов, проходов и оборудования камеры.</p>
      </div>

      <section class="tg-use-case" aria-labelledby="tgUseCaseTank">
        <figure class="tg-use-media">
          <img src="{url(tank)}" srcset="{srcset(tank)}"
            sizes="(max-width: 767px) calc(100vw - 76px), (max-width: 900px) calc(100vw - 118px), 504px"
            alt="{tank['alt']}" width="{tank['width']}" height="{tank['height']}"
            loading="lazy" decoding="async">
          <figcaption>Иллюстрация применения: окраска цилиндрической емкости из кабины подъемника 3D.</figcaption>
        </figure>
        <div class="tg-use-copy">
          <span class="tg-use-kicker">Окраска цилиндрических емкостей</span>
          <h3 id="tgUseCaseTank">Подъемник для окраски цистерн и резервуаров</h3>
          <p>При окраске крупной цистерны маляру нужен доступ к боковой поверхности и верхней части корпуса. На иллюстрации оператор работает краскопультом из кабины рядом с цилиндрической емкостью. Подъемник размещен у стены окрасочной камеры; рабочая зона находится между кабиной и поверхностью изделия.</p>
          <p>Вертикальный подъем позволяет менять высоту обработки. Движение по направляющим помогает переходить к следующему участку вдоль корпуса, а выдвижение кабины — выбирать рабочее положение у криволинейной поверхности. Расстояние распыления задают по технологии нанесения покрытия и требованиям используемого материала.</p>
          <ul class="tg-use-points">
            <li>окраска наружной поверхности цистерн и резервуаров;</li>
            <li>обработка верхних и боковых участков цилиндрических корпусов;</li>
            <li>подбор вылета кабины по диаметру изделия и ширине камеры.</li>
          </ul>
        </div>
      </section>

      <section class="tg-use-case" aria-labelledby="tgUseCaseProject">
        <div class="tg-use-copy">
          <span class="tg-use-kicker">Подбор под производственный участок</span>
          <h3 id="tgUseCaseProject">Рельсовая система 3D под размеры окрасочной камеры</h3>
          <p>Для расчета нужны размеры камеры, длина и диаметр емкости, требуемая высота обслуживания и расстояние от направляющих до изделия. Также учитывают расположение ворот, вентиляционных каналов, освещения и инженерных коммуникаций. По этим данным определяют длину пути, ход подъема, вылет и размеры рабочей кабины.</p>
          <p>Грузоподъемность и исполнение оборудования фиксируют в техническом задании с учетом массы оператора, инструмента и условий рабочей зоны. Параметры <a href="https://temir-gidro.ru/accessories/gidraulic-cylinders/">гидроцилиндров</a> подбирают по нагрузке и требуемому ходу. Возможность применения в конкретной окрасочной среде и требования к исполнению проверяют при проектировании.</p>
          <p>Для задач, где требуется только вертикальный подъем, можно рассмотреть <a href="https://temir-gidro.ru/equipment/temir-gidro-1x/">ножничный подъемник ТЕМИР ГИДРО 1X</a>. Выбор конструкции зависит от маршрута обработки и доступного места в камере.</p>
        </div>
      </section>

      <div class="tg-desc-conclusion">
        <span class="tg-conclusion-badge">Производство РФ</span>
        <span>«ТЕМИР ГИДРО» проектирует подъемники для окрасочных камер под задачи производства. Для предварительного расчета подготовьте план камеры, габариты цистерны или другого изделия, требуемую высоту обслуживания и вылет кабины.</span>
      </div>
    </div>
  </section>"""
start = html.index('<div class="tg-desc-single-col">')
end = html.index("<!-- JavaScript:")
html = html[:start] + description + "\n\n  " + html[end:]
script = """
  <script>
    (function () {
      const root = document.getElementById('tg-paint-lift-3d');
      if (!root || root.dataset.tgInitialized === 'true') return;
      root.dataset.tgInitialized = 'true';
      const gallery = root.querySelector('[data-tg-gallery]');
      if (!gallery) return;
      const mainImage = gallery.querySelector('.tg-gallery-main');
      const counter = gallery.querySelector('.tg-gallery-counter');
      const thumbs = Array.from(gallery.querySelectorAll('.tg-gallery-thumb'));
      const previous = gallery.querySelector('.tg-gallery-prev');
      const next = gallery.querySelector('.tg-gallery-next');
      if (!mainImage || !counter || !thumbs.length) return;
      let activeIndex = 0;

      function showGalleryImage(index) {
        const normalizedIndex = (index + thumbs.length) % thumbs.length;
        if (normalizedIndex === activeIndex) return;
        const button = thumbs[normalizedIndex];
        activeIndex = normalizedIndex;
        thumbs.forEach((thumb, thumbIndex) => {
          const active = thumbIndex === activeIndex;
          thumb.classList.toggle('active', active);
          thumb.setAttribute('aria-pressed', String(active));
        });
        mainImage.alt = button.dataset.alt;
        mainImage.width = Number(button.dataset.width);
        mainImage.height = Number(button.dataset.height);
        // Full-size gallery sources are separate from thumbnail files.
        mainImage.srcset = button.dataset.srcset;
        mainImage.src = button.dataset.src;
        counter.textContent = (activeIndex + 1) + ' / ' + thumbs.length;
      }

      thumbs.forEach((button, index) => {
        button.addEventListener('click', () => showGalleryImage(index));
      });
      if (previous) previous.addEventListener('click', () => showGalleryImage(activeIndex - 1));
      if (next) next.addEventListener('click', () => showGalleryImage(activeIndex + 1));
      gallery.addEventListener('keydown', event => {
        if (event.key === 'ArrowLeft') {
          event.preventDefault(); showGalleryImage(activeIndex - 1);
        } else if (event.key === 'ArrowRight') {
          event.preventDefault(); showGalleryImage(activeIndex + 1);
        } else if (event.key === 'Home') {
          event.preventDefault(); showGalleryImage(0);
        } else if (event.key === 'End') {
          event.preventDefault(); showGalleryImage(thumbs.length - 1);
        }
      });
    })();
  </script>
"""
html = re.sub(r"<script>.*?</script>", lambda _: script, html, count=1, flags=re.S)
html = html.replace("<!-- JavaScript: галерея и анимация появления -->", "<!-- JavaScript: переключение ракурсов -->")
title = "Подъемники для окрасочных камер 3D — ТЕМИР ГИДРО"
meta = "Подъемники для окрасочных камер 3D от ТЕМИР ГИДРО для окраски цистерн и емкостей. Подъем, движение вдоль изделия и выдвижение кабины. Расчет под вашу камеру."
comment = f"""<!--
WORDPRESS / YOAST
Фокусная ключевая фраза: подъемники для окрасочных камер 3D
SEO-заголовок: {title}
Meta description: {meta}
Slug: podemniki-dlya-okrasochnyh-kamer-3d
Эти значения внесите в Yoast. Комментарий не создает метатеги.
Заголовок H1 задает шаблон WordPress. Компонент содержит H2 и H3.
Загрузите все WebP-файлы из images в медиатеку. Замените все __TG_IMAGES_URL__
реальным общим URL каталога загрузок без завершающего слеша.
Использованы только четыре приложенных изображения и их уменьшенные версии.
-->"""
html = re.sub(r"^\s*<!--.*?-->", lambda _: comment, html, count=1, flags=re.S)
(ROOT / "wordpress.html").write_text(html, encoding="utf-8")
preview = f"""<!doctype html>
<html lang="ru">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="robots" content="noindex, nofollow">
  <title>{title}</title>
  <meta name="description" content="{meta}">
  <style>
    body {{ margin: 0; background: #F5F6F8; color: #0F172A; font-family: Arial, sans-serif; }}
    .preview-heading {{ max-width: 1210px; margin: 32px auto 16px; padding: 0 15px; font-size: clamp(24px, 3vw, 36px); line-height: 1.25; }}
  </style>
</head>
<body>
  <h1 class="preview-heading">Подъемники для окрасочных камер 3D</h1>
  <main>{html.replace(BASE, "images")}</main>
</body>
</html>
"""
(ROOT / "preview.html").write_text(preview, encoding="utf-8")
settings = f"""Фокусная ключевая фраза: подъемники для окрасочных камер 3D
SEO-заголовок: {title}
Meta description: {meta}
Slug: podemniki-dlya-okrasochnyh-kamer-3d
H1 страницы: Подъемники для окрасочных камер 3D
Социальное изображение Yoast: {general['name']}.webp

Внесите title, description и социальное изображение в настройки Yoast.
Slug сохраняйте, если страница уже опубликована по этому адресу.
Не меняйте адрес существующей страницы ради ключевой фразы.
В шаблоне должен быть один главный H1; компонент содержит H2 и H3.
canonical должен вести на фактический адрес страницы; его задает WordPress/Yoast.
Не добавляйте выдуманные цены, рейтинги, отзывы или сертификаты в JSON-LD.
"""
(ROOT / "seo-settings.txt").write_text(settings, encoding="utf-8")
readme = """# HTML для WordPress: подъемники для окрасочных камер 3D

Галерея содержит три приложенных изображения на белом фоне.
Фото с цистерной находится в блоке об окраске цилиндрических емкостей.
WebP и уменьшенные версии получены только из четырех приложенных PNG.
Изображения не кадрированы и не дорисованы.

## Установка

1. Загрузите все 19 WebP-файлов из images в медиатеку одним сеансом.
   Это четыре изображения и 15 уменьшенных версий для адаптивной загрузки.
   WordPress должен сохранить имена файлов. При суффиксах, добавленных к дублям,
   скорректируйте имена в HTML по фактическим адресам.
2. Скопируйте URL любого загруженного файла и удалите имя файла вместе с последним слешем.
   Получится общий префикс каталога. Например:
   https://temir-gidro.ru/wp-content/uploads/2026/10
   Это пример: используйте реальный путь своей медиатеки.
3. Замените ВСЕ вхождения __TG_IMAGES_URL__ в wordpress.html полученным префиксом.
   Если изображения оказались в разных каталогах, подставьте полные реальные URL каждого файла.
4. Замените старый компонент содержимым wordpress.html в HTML-блоке WordPress/Elementor.
   Сохраните style и script.
5. Внесите настройки из seo-settings.txt в Yoast. Главный H1 задается шаблоном страницы;
   компонент содержит H2 и H3. Назначьте общий вид изображением записи и социальным фото Yoast.
6. Проверьте три ракурса и мобильную страницу после сохранения.

preview.html — локальный предпросмотр рядом с images. Он содержит noindex и не предназначен
для публикации вместо компонента wordpress.html.

## Изменения и пределы проверки

- Старые фото и схемы заменены четырьмя приложенными изображениями.
- Сюжетный блок и его заголовок посвящены окраске цистерны.
- Добавлены описательные alt, тематический текст, естественные упоминания продукта.
- WebP-файлы используют srcset/sizes и fallback src. Размеры заданы явно.
- Главное фото загружается eager с fetchpriority=high; нижнее фото — lazy.
- Галерея переключает полноразмерные источники, а не уменьшенные миниатюры.
- Добавлены управление стрелками клавиатуры, aria-pressed и счетчик.
- Содержание видно без JavaScript. CSS ограничен уникальным ID.
- Блокирующий импорт внешних Google Fonts удален; остаются системные шрифты.
- Технические характеристики, цены, отзывы и реальные выполненные кейсы не выдуманы.
- Граф структурированных данных Yoast не дублируется.

Публичные URL фото, метатеги Yoast, индексацию и поисковые результаты проверяют после публикации.
В этом пакете проверен локальный HTML и изображения; сайт и медиатека не изменены.

Локальная проверка в Chrome: все изображения загружаются, три ракурса переключаются,
клавиатура и циклический переход работают. На ширине 1440, 390 и 320 px горизонтального
переполнения нет. Основной текст доступен без JavaScript; ошибок браузера не обнаружено.

## Проверенные рекомендации Google

Изображения: https://developers.google.com/search/docs/appearance/google-images
Title: https://developers.google.com/search/docs/appearance/title-link
Description: https://developers.google.com/search/docs/appearance/snippet
"""
(ROOT / "README.md").write_text(readme, encoding="utf-8")
(ROOT / "image-manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
assert "data:image" not in html
assert "габаритная схема" not in html
assert "схема узлов" not in html
assert len(manifest) == 19
archive = ROOT.parent / "paint-lift-3d-wordpress.zip"
with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as bundle:
    for filename in ("wordpress.html", "preview.html", "seo-settings.txt", "README.md", "image-manifest.json"):
        bundle.write(ROOT / filename, f"paint-lift-3d-wordpress/{filename}")
    for path in sorted(IMAGES.glob("*.webp")):
        bundle.write(path, f"paint-lift-3d-wordpress/images/{path.name}")
print(json.dumps(dict(
    source_html_bytes=SOURCE.stat().st_size,
    wordpress_html_bytes=(ROOT / "wordpress.html").stat().st_size,
    images_count=len(manifest), all_image_bytes=sum(v["bytes"] for v in manifest),
    largest_webp_bytes=max(v["bytes"] for v in manifest), meta_characters=len(meta),
    archive=str(archive)), ensure_ascii=False, indent=2))

