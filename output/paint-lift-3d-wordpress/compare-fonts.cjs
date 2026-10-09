const {chromium} = require('C:/Users/user/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
(async()=>{
  const reports=[];
  const browser=await chromium.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:true});
  const page=await browser.newPage({viewport:{width:1440,height:1000}});
  await page.route(/^https?:\/\//,route=>route.abort());
  for(const [label,url,id] of [
    ['2D','file:///C:/Users/user/Downloads/Подъемники для окрасочных камер 2D - ТЕМИР ГИДРО.html','tg-paint-lift-2d'],
    ['3D','file:///C:/projects/temir-gidro/output/paint-lift-3d-wordpress/preview-webp-inline.html','tg-paint-lift-3d'],
    ['3D fixed','file:///C:/projects/temir-gidro/output/paint-lift-3d-wordpress/preview-webp-inline-fonts-fixed.html','tg-paint-lift-3d']
  ]){
    await page.goto(url,{waitUntil:'load'});
    await page.evaluate(()=>document.fonts.ready);
    const styles=await page.evaluate(id=>['.tg-product-title','.tg-section-title','.tg-use-copy h3','.tg-product-desc','.tg-use-copy p'].map(selector=>{
      const node=document.querySelector('#'+id+' '+selector); const css=getComputedStyle(node);
      return {selector,fontFamily:css.fontFamily,fontWeight:css.fontWeight,fontSize:css.fontSize,lineHeight:css.lineHeight,textShadow:css.textShadow,fontSynthesis:css.fontSynthesis};
    }),id);
    const client=await page.context().newCDPSession(page);
    await client.send('DOM.enable'); await client.send('CSS.enable');
    const {root}=await client.send('DOM.getDocument',{depth:1});
    const fonts=[];
    for(const selector of ['.tg-product-title','.tg-use-copy h3','.tg-product-desc']){
      const {nodeId}=await client.send('DOM.querySelector',{nodeId:root.nodeId,selector:'#'+id+' '+selector});
      fonts.push({selector,...await client.send('CSS.getPlatformFontsForNode',{nodeId})});
    }
    reports.push({label,styles,fonts});
    if(label==='3D fixed') {
      await page.locator('.tg-hero-grid').screenshot({path:__dirname+'/qa/hero-fonts-fixed.png'});
      await page.setViewportSize({width:390,height:844});
      await page.locator('.tg-use-media').scrollIntoViewIfNeeded();
      await page.waitForFunction(()=>Array.from(document.images).every(i=>i.complete&&i.naturalWidth>0));
      if(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth)) throw new Error('Mobile overflow');
      await page.evaluate(()=>scrollTo(0,0));
      await page.screenshot({path:__dirname+'/qa/mobile-fonts-fixed.png',fullPage:true});
    }
    await client.detach();
  }
  for(let i=0;i<2;i++) {
    const expected=reports[0].fonts[i].fonts.map(f=>f.postScriptName);
    const actual=reports[2].fonts[i].fonts.map(f=>f.postScriptName);
    if(JSON.stringify(expected)!==JSON.stringify(actual)) throw new Error('Fonts differ from 2D reference');
  }
  require('fs').writeFileSync(__dirname+'/qa/font-comparison.json',JSON.stringify(reports,null,2));
  console.log(JSON.stringify(reports.map(r=>({label:r.label,titleWeight:r.styles[0].fontWeight,titleFonts:r.fonts[0].fonts.map(f=>f.postScriptName)})),null,2));
  await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});

