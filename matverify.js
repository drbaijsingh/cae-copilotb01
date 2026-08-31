const { chromium } = require('playwright');
const REF = {
  fgm:{zns_h:0.1349756304409094, D:13822.866004425006, I0:32.51, f11:64.77992442270258},
  lam:{h_mm:1.0, D11:8.236496053751779, D12:1.1902975430340774, D66:1.556647576854897, f11:5.412395519921578},
  sw:{D:8401.298884409647, S:1050625.0, fb:275.4210938849189, fs:241.73233936362976, ratio:0.298150030178951}
};
const near=(a,b,tol)=>Math.abs(a-b)/Math.abs(b)<tol;
(async()=>{
  const br=await chromium.launch(); const p=await br.newPage({viewport:{width:1400,height:1100}});
  const errs=[]; p.on('pageerror',e=>errs.push(e.message));
  p.on('console',m=>{if(m.type()==='error'&&!/ERR_TUNNEL|ERR_NAME/.test(m.text()))errs.push('C:'+m.text());});
  await p.goto('file:///home/claude/mat.html'); await p.waitForTimeout(600);

  const num=s=>parseFloat(String(s).replace(/[^0-9eE.+-]/g,''));
  const got=await p.evaluate(()=>({
    zns:document.getElementById('fgZns').textContent,
    D:document.getElementById('fgD11').textContent,
    I0:document.getElementById('fgI0').textContent,
    f:document.getElementById('fgF1').textContent,
    B:document.getElementById('fgB11').textContent
  }));
  console.log('--- FGM (Al2O3/Al, power n=1, Mori-Tanaka, h=10mm) ---');
  const checks=[];
  checks.push(['z_ns/h', num(got.zns), REF.fgm.zns_h, 1e-4]);
  checks.push(['D',      num(got.D),   REF.fgm.D,     1e-4]);
  checks.push(['I0',     num(got.I0),  REF.fgm.I0,    1e-4]);
  checks.push(['f11',    num(got.f),   REF.fgm.f11,   1e-4]);
  checks.forEach(([n,g,r,t])=>console.log(`  ${n.padEnd(8)} js=${g}  py=${r.toPrecision(8)}  ${near(g,r,t)?'MATCH':'*** MISMATCH ***'}`));
  console.log('  B =', got.B);

  await p.evaluate(()=>document.querySelector('[data-panel="p-lam"]').click());
  await p.waitForTimeout(250);
  const gl=await p.evaluate(()=>{
    const cells=[...document.querySelectorAll('#lamABD table')][2].querySelectorAll('td');
    return {h:document.getElementById('lamH').textContent, f:document.getElementById('lamF1').textContent,
            D11:cells[0].textContent, D12:cells[1].textContent, D66:cells[8].textContent,
            flags:[...document.querySelectorAll('#lamFlags .flag')].map(f=>f.className.split(' ')[1]+': '+f.textContent.trim().slice(1,58))};
  });
  console.log('\n--- Laminate [0/45/-45/90]s AS4 ---');
  [['h_mm',num(gl.h),REF.lam.h_mm],['D11',num(gl.D11),REF.lam.D11],['D12',num(gl.D12),REF.lam.D12],
   ['D66',num(gl.D66),REF.lam.D66],['f11',num(gl.f),REF.lam.f11]]
   .forEach(([n,g,r])=>console.log(`  ${n.padEnd(6)} js=${g}  py=${r.toPrecision(8)}  ${near(g,r,1e-3)?'MATCH':'*** MISMATCH ***'}`));
  gl.flags.forEach(f=>console.log('  flag',f));

  await p.evaluate(()=>document.querySelector('[data-panel="p-sand"]').click());
  await p.waitForTimeout(250);
  const gs=await p.evaluate(()=>({
    D:document.getElementById('swD').textContent, S:document.getElementById('swS').textContent,
    fb:document.getElementById('swFb').textContent, fs:document.getElementById('swF1').textContent,
    r:document.getElementById('swR').textContent, err:document.getElementById('swErr').textContent,
    gov:(document.querySelector('#swFail .flag')||{textContent:''}).textContent.trim()
  }));
  console.log('\n--- Sandwich (Al faces 0.5mm / foam core 20mm) ---');
  [['D',num(gs.D),REF.sw.D],['S',num(gs.S),REF.sw.S],['f_bend',num(gs.fb),REF.sw.fb],
   ['f_shear',num(gs.fs),REF.sw.fs],['Dk2/S',num(gs.r),REF.sw.ratio]]
   .forEach(([n,g,r])=>console.log(`  ${n.padEnd(8)} js=${g}  py=${r.toPrecision(8)}  ${near(g,r,1e-3)?'MATCH':'*** MISMATCH ***'}`));
  console.log('  shear error:',gs.err);
  console.log(' ',gs.gov);

  // exercise every solver x law x scheme for JS errors
  let n=0;
  for(const tab of ['p-fgm','p-lam','p-sand']){
    await p.evaluate(t=>document.querySelector(`[data-panel="${t}"]`).click(),tab);
    for(let i=0;i<3;i++){
      await p.evaluate(([t,i])=>{
        const host={p_fgm:'fgSolverSeg',p_lam:'lamSolverSeg',p_sand:'swSolverSeg'}[t.replace(/-/g,'_')];
        document.querySelectorAll('#'+host+' .segbtn')[i].click();
      },[tab,i]);
      await p.waitForTimeout(80); n++;
    }
  }
  await p.evaluate(()=>document.querySelector('[data-panel="p-fgm"]').click());
  for(let li=0;li<3;li++) for(let si=0;si<3;si++){
    await p.evaluate(([li,si])=>{
      document.querySelectorAll('#fgLawSeg .segbtn')[li].click();
      document.querySelectorAll('#fgSchemeSeg .segbtn')[si].click();
    },[li,si]); await p.waitForTimeout(50); n++;
  }
  // bad stacking input
  await p.evaluate(()=>{document.querySelector('[data-panel="p-lam"]').click();
    const i=document.getElementById('lamSeq'); i.value='garbage'; i.dispatchEvent(new Event('input'));});
  await p.waitForTimeout(150);
  const badOk=await p.evaluate(()=>document.querySelectorAll('#lamStack .flag-err').length>0);
  console.log('\ncombinations exercised:',n);
  console.log('invalid stacking handled gracefully:',badOk?'yes':'NO');
  console.log('JS errors:',errs.length); errs.forEach(e=>console.log('  ',e));
  await br.close();
})();
