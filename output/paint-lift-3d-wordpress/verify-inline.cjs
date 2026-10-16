const path = require('path');
const fs = require('fs');
const {chromium} = require('C:/Users/user/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
(async () => {
  const browser = await chromium.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe', headless:true});
  const page = await browser.newPage({viewport:{width:1440,height:1000}});
  const requests = [];
  const errors = [];
  page.on('request', request => requests.push(request.url().slice(0,120)));
  page.on('pageerror', error => errors.push(String(error)));
  await page.goto('file:///' + __dirname.replace(/\\/g,'/') + '/preview-webp-inline.html');
  await page.locator('.tg-use-media').scrollIntoViewIfNeeded();
  await page.waitForFunction(() => Array.from(document.images).every(image=>image.complete && image.naturalWidth>0));
  const images = await page.evaluate(() => Array.from(document.images).map(image=>({
    webpInline:image.getAttribute('src').startsWith('data:image/webp;base64,'),
    loaded:image.complete && image.naturalWidth>0
  })));
  if (images.length !== 5 || images.some(image=>!image.webpInline||!image.loaded)) throw new Error('Embedded images failed');
  for(let index=0;index<3;index++) {
    await page.locator('.tg-gallery-thumb').nth(index).click();
    await page.waitForFunction(() => {
      const image=document.querySelector('.tg-gallery-main');
      return image.complete && image.naturalWidth >= 1500;
    });
    if(await page.locator('.tg-gallery-counter').textContent() !== (index+1)+' / 3') throw new Error('Gallery failed');
  }
  await page.locator('.tg-gallery-next').click();
  if(await page.locator('.tg-gallery-counter').textContent() !== '1 / 3') throw new Error('Gallery wrap failed');
  await page.setViewportSize({width:390,height:844});
  await page.evaluate(()=>scrollTo(0,0));
  const overflow = await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth);
  if (overflow || errors.length || requests.length!==1) throw new Error('Unexpected overflow, error or external request');
  await page.screenshot({path:path.join(__dirname,'qa','mobile-webp-inline.png'),fullPage:true});
  const report={imagesLoaded:images.length,galleryViews:3,mobileOverflow:overflow,externalImageRequests:0,browserErrors:errors};
  fs.writeFileSync(path.join(__dirname,'qa','verification-webp-inline.json'),JSON.stringify(report,null,2));
  console.log(JSON.stringify(report));
  await browser.close();
})().catch(error=>{console.error(error);process.exit(1);});

