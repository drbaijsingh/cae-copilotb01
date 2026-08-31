const { chromium } = require('playwright');
// Leissa frequency parameters, square isotropic plate, nu=0.3
const LEISSA={SSSS:19.7392,SCSC:28.9509,SSSC:23.6463,SFSF:9.6314,SCSF:12.6874,SSSF:11.6845,
              CCCC:35.9852,CCCF:24.0200,CFFF:3.4917,CCFF:6.9421};
(async()=>{
  const br=await chromium.launch(); const p=await br.newPage({viewport:{width:1400,height:1200}});
  const errs=[]; p.on('pageerror',e=>errs.push(e.message));
  await p.goto('file:///home/claude/mat.html'); await p.waitForTimeout(700);

  // Drive the FGM tab to a HOMOGENEOUS plate (n=0 -> pure ceramic) so we can
  // compare directly against Leissa's isotropic values.
  const res=await p.evaluate(async(LEISSA)=>{
    const set=(id,v)=>{const e=document.getElementById(id);e.value=v;e.dispatchEvent(new Event('input'));};
    const sel=(id,v)=>{const e=document.getElementById(id);e.value=v;e.dispatchEvent(new Event('change'));};
    set('fgN',0); set('fgA',1); set('fgB',1); set('fgH',0.005);
    await new Promise(r=>setTimeout(r,60));
    const out=[];
    for(const code of Object.keys(LEISSA)){
      sel('fgEx0',code[0]); sel('fgEy0',code[1]); sel('fgEx1',code[2]); sel('fgEy1',code[3]);
      await new Promise(r=>setTimeout(r,140));
      const f=parseFloat(document.getElementById('fgF1').textContent);
      const method=document.getElementById('fgMethodNote').textContent;
      out.push({code,f,method});
    }
    return out;
  },LEISSA);

  // Convert Hz -> lambda using the ceramic (Al2O3) properties the tool used
  const E=380e9,nu=0.30,rho=3800,h=0.005,a=1;
  const D=E*h**3/(12*(1-nu*nu)), I0=rho*h;
  const sc=a*a*Math.sqrt(I0/D)*2*Math.PI;
  console.log('Homogeneous plate (n=0 -> pure Al2O3), a=b=1 m, h=5 mm, nu=0.30');
  console.log('lambda = omega a^2 sqrt(rho h / D)   vs Leissa (1969)\n');
  console.log('case    lambda      Leissa     err %    method');
  let worst=0;
  for(const r of res){
    const lam=r.f*sc, ref=LEISSA[r.code], err=100*(lam-ref)/ref;
    if(Math.abs(err)>Math.abs(worst))worst=err;
    console.log(`${r.code}  ${lam.toFixed(4).padStart(9)} ${ref.toFixed(4).padStart(10)} ${err>=0?'+':''}${err.toFixed(3).padStart(7)}   ${r.method.split(',')[0]}`);
  }
  console.log(`\nworst error: ${worst>=0?'+':''}${worst.toFixed(3)}%`);
  console.log('JS errors:',errs.length); errs.forEach(e=>console.log(' ',e));
  await br.close();
})();
