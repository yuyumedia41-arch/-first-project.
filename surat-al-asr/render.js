const {chromium}=require('playwright');
const {spawn}=require('child_process');
const FPS=30, DUR=167.0, N=Math.round(FPS*DUR), WORKERS=4;
async function worker(w,a,b){
  const br=await chromium.launch(); const p=await br.newPage({viewport:{width:1920,height:1080}});
  await p.goto('file://'+__dirname+'/index.html'); await p.evaluate(()=>document.fonts.ready);
  const ff=spawn('ffmpeg',['-hide_banner','-loglevel','error','-y','-f','image2pipe','-framerate',String(FPS),'-c:v','mjpeg','-i','-','-c:v','libx264','-preset','medium','-crf','16','-pix_fmt','yuv420p',`${__dirname}/chunk${w}.mp4`]);
  for(let i=a;i<b;i++){
    await p.evaluate(t=>seek(t),i/FPS);
    const buf=await p.screenshot({type:'jpeg',quality:95});
    if(!ff.stdin.write(buf)) await new Promise(r=>ff.stdin.once('drain',r));
    if((i-a)%100===0) console.log(`w${w} ${i-a}/${b-a}`);
  }
  ff.stdin.end(); await new Promise(r=>ff.on('close',r)); await br.close();
}
(async()=>{
  const per=Math.ceil(N/WORKERS); const jobs=[];
  for(let w=0;w<WORKERS;w++) jobs.push(worker(w,w*per,Math.min(N,(w+1)*per)));
  await Promise.all(jobs); console.log('done',N);
})();
