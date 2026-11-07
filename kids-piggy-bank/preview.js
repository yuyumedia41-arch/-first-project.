const {chromium}=require('playwright');
(async()=>{
 const times=process.argv.slice(2).map(Number);
 const b=await chromium.launch(); const p=await b.newPage({viewport:{width:1920,height:1080}});
 const errs=[]; p.on('pageerror',e=>errs.push(e.message)); p.on('console',m=>{if(m.type()==='error')errs.push(m.text())});
 await p.goto('file://'+__dirname+'/index.html'); await p.evaluate(()=>document.fonts.ready);
 for(const t of times){await p.evaluate(t=>seek(t),t); await p.screenshot({path:`${__dirname}/prev/f_${t.toFixed(2).padStart(5,'0')}.jpg`,type:'jpeg',quality:80});}
 console.log(errs.join('\n')||'no errors'); await b.close();
})();
