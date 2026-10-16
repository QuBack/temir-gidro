const fs = require('fs');
const path = require('path');
const {chromium} = require('C:/Users/user/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const root = __dirname;
const qa = path.join(root, 'qa');
fs.mkdirSync(qa, {recursive:true});
(async () => {
  const browser = await chromium.launch({
    executablePath: 'C:/Program Files/Google/Chrome/Application/chrome.exe',
    headless: true,
    args: ['--disable-extensions','--no-first-run','--no-default-browser-check']
  });
  const page = await browser.newPage({viewport:{width:1440,height:1000}});
  const errors = [];
  page.on('pageerror', err => errors.push(String(err)));
  page.on('requestfailed', request => errors.push(request.url() + ': ' + request.failure().errorText));
  await page.goto('file:///' + root.replace(/\\/g,'/') + '/preview.html', {waitUntil:'load'});
  await page.locator('.tg-use-media').scrollIntoViewIfNeeded();
  await page.waitForFunction(() => Array.from(document.images).every(img => img.complete && img.naturalWidth > 0));
  await page.evaluate(() => scrollTo(0,0));
  const inspect = async () => page.evaluate(() => ({
    overflow: document.documentElement.scrollWidth > innerWidth,
    imageCount: document.images.length,
    h1Count: document.querySelectorAll('h1').length,
    galleryThumbs: document.querySelectorAll('.tg-gallery-thumb').length,
    images: Array.from(document.images).map(i => ({alt:i.alt, src:i.currentSrc, loaded:i.complete && i.naturalWidth>0,
      width:i.getAttribute('width'), height:i.getAttribute('height'), loading:i.loading, fetchpriority:i.getAttribute('fetchpriority')}))
  }));
  const desktop = await inspect();
  await page.screenshot({path:path.join(qa,'desktop.png'),fullPage:true});
  await page.locator('.tg-hero-grid').screenshot({path:path.join(qa,'hero-desktop.png')});
  await page.locator('.tg-use-case').first().screenshot({path:path.join(qa,'tank-desktop.png')});
  const gallery = [];
  for (let i=0;i<3;i++) {
    await page.locator('.tg-gallery-thumb').nth(i).click();
    await page.waitForFunction(() => {const image=document.querySelector('.tg-gallery-main'); return image.complete && image.naturalWidth>0;});
    const state = await page.evaluate(() => ({
      src:document.querySelector('.tg-gallery-main').getAttribute('src'),
      counter:document.querySelector('.tg-gallery-counter').textContent,
      pressed:Array.from(document.querySelectorAll('.tg-gallery-thumb')).map(b=>b.getAttribute('aria-pressed'))
    }));
    if (state.counter !== (i+1) + ' / 3' || state.pressed.filter(v=>v==='true').length!==1) throw new Error('Gallery state mismatch');
    if (/-240\.webp$/.test(state.src)) throw new Error('Full gallery uses thumbnail');
    gallery.push(state);
  }
  await page.locator('.tg-gallery-next').click();
  if (await page.locator('.tg-gallery-counter').textContent() !== '1 / 3') throw new Error('Gallery wrap failed');
  await page.locator('.tg-gallery-thumb').first().focus();
  await page.keyboard.press('End');
  if (await page.locator('.tg-gallery-counter').textContent() !== '3 / 3') throw new Error('Keyboard End failed');
  await page.keyboard.press('ArrowRight');
  if (await page.locator('.tg-gallery-counter').textContent() !== '1 / 3') throw new Error('Keyboard right failed');
  await page.setViewportSize({width:390,height:844});
  await page.locator('.tg-use-media').scrollIntoViewIfNeeded();
  await page.waitForFunction(() => Array.from(document.images).every(img=>img.complete&&img.naturalWidth>0));
  await page.evaluate(() => scrollTo(0,0));
  const mobile = await inspect();
  await page.screenshot({path:path.join(qa,'mobile.png'),fullPage:true});
  await page.setViewportSize({width:320,height:740});
  const narrow = await inspect();
  const noJsContext = await browser.newContext({javaScriptEnabled:false,viewport:{width:390,height:844}});
  const noJs = await noJsContext.newPage();
  await noJs.goto('file:///' + root.replace(/\\/g,'/') + '/preview.html');
  const staticVisible = await noJs.locator('#tgUseCaseTank').isVisible();
  const wordpress = fs.readFileSync(path.join(root,'wordpress.html'),'utf8');
  if (desktop.overflow || mobile.overflow || narrow.overflow) throw new Error('Horizontal overflow');
  if (desktop.imageCount!==5 || desktop.galleryThumbs!==3 || desktop.h1Count!==1) throw new Error('Unexpected content structure');
  if (/data:image/.test(wordpress) || /<h1\b/.test(wordpress) || /noindex/.test(wordpress)) throw new Error('WordPress content issue');
  if (!staticVisible || errors.length) throw new Error('Visibility or browser error: ' + JSON.stringify(errors));
  const report={desktop,mobile,narrow,gallery,noJavaScriptContentVisible:staticVisible,browserErrors:errors};
  fs.writeFileSync(path.join(qa,'verification.json'),JSON.stringify(report,null,2));
  console.log(JSON.stringify({desktopOverflow:desktop.overflow,mobileOverflow:mobile.overflow,narrowOverflow:narrow.overflow,
    imageCount:desktop.imageCount,galleryClicks:gallery.length,keyboardPassed:true,noJavaScriptContentVisible:staticVisible,browserErrors:errors}));
  await browser.close();
})().catch(err=>{console.error(err);process.exit(1);});

