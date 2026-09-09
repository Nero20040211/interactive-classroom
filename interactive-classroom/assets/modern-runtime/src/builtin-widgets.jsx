import React, { useMemo, useState } from "react";
import {
  EquationWidget,
  MotionLabWidget,
  ProcessAnimationWidget,
  SimulationWidget,
} from "./animation-widgets.jsx";

const panel = "rounded-xl border border-black/10 bg-black/[0.02] p-4 dark:border-white/15 dark:bg-white/[0.035]";
const button = "min-h-10 rounded-lg border border-black/15 px-3 py-2 text-sm dark:border-white/20";

function cfgOf(scene){ return scene?.content?.widgetConfig || {}; }
function clamp(n,a,b){ return Math.max(a,Math.min(b,n)); }
function num(v,d=0){ const n=Number(v); return Number.isFinite(n)?n:d; }
function lcg(seed){ let s=(num(seed,1)>>>0)||1; return ()=>((s=(1664525*s+1013904223)>>>0)/4294967296); }
export function RandomTrialWidget({ scene }){
 const cfg=cfgOf(scene); const [trials,setTrials]=useState(num(cfg.initialTrials,80)); const [nonce,setNonce]=useState(0); const p=clamp(num(cfg.theoreticalP,.5),0,1);
 const result=useMemo(()=>{const r=lcg(num(cfg.seed,1)+nonce*9973); let hit=0; const pts=[]; for(let i=1;i<=trials;i++){if(r()<p)hit++; if(i===1||i%Math.max(1,Math.floor(trials/60))===0||i===trials)pts.push([i,hit/i]);} return {hit,freq:trials?hit/trials:0,pts};},[trials,nonce,p,cfg.seed]);
 const points=result.pts.map(([x,y])=>`${20+(x/Math.max(1,trials))*560},${180-(y*140)}`).join(" ");
 return <section className={panel} data-modern-widget="random-trial-lab"><h3 className="font-semibold">随机试验</h3><p className="mt-2 text-sm/7">{cfg.question || "调节试验次数，比较有限频率与理论概率。"}</p><label className="mt-4 block text-sm">试验次数：{trials}<input className="mt-2 w-full" type="range" min={num(cfg.minTrials,20)} max={num(cfg.maxTrials,1200)} step={num(cfg.step,20)} value={trials} onChange={e=>setTrials(Number(e.target.value))}/></label><svg viewBox="0 0 600 200" className="mt-3 w-full" role="img" aria-label="累计频率曲线"><line x1="20" y1={180-p*140} x2="580" y2={180-p*140} stroke="currentColor" strokeDasharray="6 6" opacity=".35"/><polyline points={points} fill="none" stroke="currentColor" strokeWidth="3"/></svg><p className="text-sm">本次成功 {result.hit}/{trials}，累计频率 {result.freq.toFixed(3)}；理论概率 {p.toFixed(3)}。</p><button className={`${button} mt-3`} type="button" onClick={()=>setNonce(n=>n+1)}>重新模拟</button>{cfg.boundary&&<p className="mt-3 text-sm opacity-70">边界：{cfg.boundary}</p>}</section>;
}

export function FbdWidget({ scene }){
 const cfg=cfgOf(scene); const [picked,setPicked]=useState([]); const target=cfg.targetForceIds||[]; const correct=picked.length===target.length&&picked.every(x=>target.includes(x));
 return <section className={panel} data-modern-widget="fbd-lab"><h3 className="font-semibold">受力分析</h3><p className="mt-2 text-sm/7">{cfg.prompt}</p><div className="mt-3 grid gap-2 sm:grid-cols-2">{(cfg.candidateForces||[]).map(f=><label key={f.id} className="rounded-lg border border-black/10 p-3 text-sm dark:border-white/15"><input type="checkbox" checked={picked.includes(f.id)} onChange={()=>setPicked(xs=>xs.includes(f.id)?xs.filter(x=>x!==f.id):[...xs,f.id])}/> <strong>{f.label}</strong><span className="block mt-1 opacity-70">{f.source}</span></label>)}</div><p className="mt-3 text-sm" role="status">{picked.length?(correct?cfg.correctFeedback:cfg.incorrectFeedback):cfg.motionNote}</p></section>;
}

export function CircuitWidget({ scene }){
 const cfg=cfgOf(scene); const base=cfg.resistors||[]; const [values,setValues]=useState(Object.fromEntries(base.map(r=>[r.id,num(r.value,1)]))); const total=base.reduce((a,r)=>a+num(values[r.id],0),0); const current=total?num(cfg.sourceVoltage,0)/total:0;
 return <section className={panel} data-modern-widget="circuit-lab"><h3 className="font-semibold">串联电路实验</h3><p className="mt-2 text-sm/7">{cfg.instructions}</p>{base.map(r=><label key={r.id} className="mt-3 block text-sm">{r.label}: {values[r.id]} {r.unit}<input className="mt-2 w-full" type="range" min={r.min} max={r.max} step={r.step} value={values[r.id]} onChange={e=>setValues(v=>({...v,[r.id]:Number(e.target.value)}))}/></label>)}<p className="mt-4 text-sm"><strong>等效电阻：</strong>{total.toFixed(2)} Ω　<strong>总电流：</strong>{current.toFixed(3)} A</p>{cfg.assumption&&<p className="mt-2 text-sm opacity-70">假设：{cfg.assumption}</p>}</section>;
}

export function MapWidget({ scene }){
 const cfg=cfgOf(scene); const points=cfg.points||[]; const [selected,setSelected]=useState(points[0]?.id||null); const pt=points.find(p=>p.id===selected);
 return <section className={panel} data-modern-widget="map-lab"><h3 className="font-semibold">空间关系实验</h3><p className="mt-2 text-sm/7">{cfg.spatialTask}</p><svg viewBox="0 0 720 360" className="mt-4 w-full rounded-xl border border-black/10 dark:border-white/10" role="img" aria-label="经纬度教学图">{[-120,-60,0,60,120].map(l=><line key={`lon${l}`} x1={(l+180)*2} y1="0" x2={(l+180)*2} y2="360" stroke="currentColor" opacity=".12"/>)}{[-60,-30,0,30,60].map(l=><line key={`lat${l}`} x1="0" y1={(90-l)*2} x2="720" y2={(90-l)*2} stroke="currentColor" opacity=".12"/>)}{points.map(p=><g key={p.id} onClick={()=>setSelected(p.id)} role="button" tabIndex="0"><circle cx={(num(p.lon)+180)*2} cy={(90-num(p.lat))*2} r={p.id===selected?9:6} fill="currentColor"/><text x={(num(p.lon)+180)*2+10} y={(90-num(p.lat))*2-8} fontSize="13">{p.name}</text></g>)}</svg>{pt&&<p className="mt-3 text-sm"><strong>{pt.name}</strong>：经度 {pt.lon}°，纬度 {pt.lat}°。{pt.properties?` ${Object.values(pt.properties).join("；")}`:""}</p>}<p className="mt-2 text-xs opacity-65">{cfg.coordinateSystem} · {cfg.projection} · {cfg.scaleNote}</p></section>;
}

export function CodeTraceWidget({ scene }){
 const cfg=cfgOf(scene); const steps=cfg.traceSteps||[]; const [i,setI]=useState(0); const st=steps[i]||{};
 return <section className={panel} data-modern-widget="code"><h3 className="font-semibold">确定性代码跟踪</h3><p className="mt-2 text-sm/7">{cfg.task}</p><pre className="mt-3 overflow-auto rounded-lg bg-black/90 p-4 text-sm text-white"><code>{cfg.code}</code></pre>{steps.length?<div className="mt-3 rounded-lg border border-black/10 p-3 text-sm dark:border-white/15"><strong>步骤 {i+1} · 行 {st.line}</strong><p className="mt-1">{st.explanation}</p>{st.state&&<code className="mt-2 block whitespace-pre-wrap">{JSON.stringify(st.state)}</code>}</div>:null}<div className="mt-3 flex gap-2"><button className={button} disabled={i<=0} onClick={()=>setI(x=>Math.max(0,x-1))}>←</button><button className={button} disabled={i>=steps.length-1} onClick={()=>setI(x=>Math.min(steps.length-1,x+1))}>→</button></div></section>;
}

export function StatsWidget({ scene }){
 const cfg=cfgOf(scene); const [mean,setMean]=useState(num(cfg.mean,0)); const [sd,setSd]=useState(Math.max(.1,num(cfg.sd,1))); const [threshold,setThreshold]=useState(num(cfg.threshold,1)); const z=(threshold-mean)/sd;
 return <section className={panel} data-modern-widget="stats-lab"><h3 className="font-semibold">统计参数实验</h3><p className="mt-2 text-sm/7">{cfg.interpretationPrompt}</p>{[["均值",mean,setMean,-4,4,.1],["标准差",sd,setSd,.2,4,.1],["阈值",threshold,setThreshold,-4,4,.1]].map(([label,val,set,min,max,step])=><label key={label} className="mt-3 block text-sm">{label}: {Number(val).toFixed(1)}<input className="mt-2 w-full" type="range" min={min} max={max} step={step} value={val} onChange={e=>set(Number(e.target.value))}/></label>)}<p className="mt-4 text-sm">当前阈值相对分布中心的标准化位置 z = {z.toFixed(2)}。比较这个相对位置，而不是只比较绝对阈值。</p></section>;
}

export function DataLabWidget({ scene }){
 const cfg=cfgOf(scene); const params=cfg.parameters||[]; const [vals,setVals]=useState(Object.fromEntries(params.map(p=>[p.id,num(p.initial,0)]))); const rows=cfg.rows||[]; const mse=rows.length&&cfg.model?.kind==="linear-regression"?rows.reduce((a,r)=>{const yhat=num(vals.beta0)+num(vals.beta1)*num(r[cfg.xKey]); return a+(yhat-num(r[cfg.yKey]))**2;},0)/rows.length:null;
 return <section className={panel} data-modern-widget="data-lab"><h3 className="font-semibold">{cfg.title || "数据实验"}</h3><p className="mt-2 text-sm/7">{cfg.prompt}</p>{params.map(p=><label key={p.id} className="mt-3 block text-sm">{p.label}: {vals[p.id]}<input className="mt-2 w-full" type="range" min={p.min} max={p.max} step={p.step} value={vals[p.id]} onChange={e=>setVals(v=>({...v,[p.id]:Number(e.target.value)}))}/></label>)}{mse!=null&&<p className="mt-3 text-sm">当前 MSE：{mse.toFixed(2)}</p>}<p className="mt-2 text-xs opacity-65">{cfg.provenance}</p></section>;
}

export function GeneticsWidget({ scene }){
 const cfg=cfgOf(scene); const allowed=cfg.allowedGenotypes||[cfg.parentA,cfg.parentB].filter(Boolean); const [a,setA]=useState(cfg.parentA||allowed[0]); const [b,setB]=useState(cfg.parentB||allowed[0]);
 const gametes=g=>String(g||"").split(""); const outcomes=useMemo(()=>{const xs=[]; for(const x of gametes(a))for(const y of gametes(b))xs.push([x,y].sort((q,w)=>q===q.toUpperCase()?-1:1).join("")); return xs;},[a,b]);
 const counts=outcomes.reduce((m,x)=>(m[x]=(m[x]||0)+1,m),{});
 return <section className={panel} data-modern-widget="genetics-lab"><h3 className="font-semibold">遗传组合实验</h3><p className="mt-2 text-sm/7">{cfg.prompt}</p><div className="mt-3 flex gap-3">{[["亲本 A",a,setA],["亲本 B",b,setB]].map(([l,v,set])=><label key={l} className="text-sm">{l}<select value={v} onChange={e=>set(e.target.value)} className="ml-2 rounded border border-black/15 bg-[var(--ic-paper)] p-2 dark:border-white/20">{allowed.map(g=><option key={g}>{g}</option>)}</select></label>)}</div><p className="mt-4 text-sm">后代组合：{Object.entries(counts).map(([g,c])=>`${g} ${c}/${outcomes.length}`).join("；")}</p><p className="mt-2 text-sm opacity-70">{cfg.phenotypeMap}</p></section>;
}

export function ClozeWidget({ scene }){
 const cfg=cfgOf(scene); const blanks=(cfg.segments||[]).filter(x=>x.blank).map(x=>x.blank); const [answers,setAnswers]=useState({}); const check=blanks.length&&blanks.every(b=>(b.answers||[]).map(x=>String(x).toLowerCase()).includes(String(answers[b.id]||"").trim().toLowerCase()));
 return <section className={panel} data-modern-widget="cloze-lab"><h3 className="font-semibold">{cfg.title || "填空实验"}</h3><p className="mt-2 text-sm/7">{cfg.prompt}</p><div className="mt-4 text-lg/9">{(cfg.segments||[]).map((seg,i)=>seg.text?<span key={i}>{seg.text}</span>:<input key={seg.blank.id} aria-label={seg.blank.label} value={answers[seg.blank.id]||""} onChange={e=>setAnswers(v=>({...v,[seg.blank.id]:e.target.value}))} className="mx-1 w-32 rounded border border-black/20 bg-transparent px-2 py-1 dark:border-white/20" />)}</div><p className="mt-3 text-sm">{Object.keys(answers).length?(check?cfg.feedback:"继续根据语义和结构检查空格。"):(cfg.strategies||[]).join("；")}</p>{cfg.boundary&&<p className="mt-2 text-xs opacity-65">{cfg.boundary}</p>}</section>;
}

export function SentenceBuilderWidget({ scene }){
 const cfg=cfgOf(scene); const tokens=cfg.tokens||[]; const [order,setOrder]=useState([]); const pick=id=>setOrder(xs=>xs.includes(id)?xs:[...xs,id]); const reset=()=>setOrder([]); const correct=JSON.stringify(order)===JSON.stringify(cfg.targetOrder||[]);
 return <section className={panel} data-modern-widget="sentence-builder-lab"><h3 className="font-semibold">句子构造</h3><p className="mt-2 text-sm/7">{cfg.prompt}</p><div className="mt-3 flex min-h-12 flex-wrap gap-2 rounded-lg border border-dashed border-black/20 p-3 dark:border-white/20">{order.map(id=><span key={id} className="rounded bg-black/5 px-2 py-1 text-sm dark:bg-white/5">{tokens.find(t=>t.id===id)?.label}</span>)}</div><div className="mt-3 flex flex-wrap gap-2">{tokens.map(t=><button className={button} type="button" key={t.id} disabled={order.includes(t.id)} onClick={()=>pick(t.id)}>{t.label}</button>)}</div><div className="mt-3 flex gap-2"><button className={button} type="button" onClick={reset}>重置</button><span className="self-center text-sm">{order.length===tokens.length?(correct?cfg.correctFeedback:cfg.incorrectFeedback):"按语义块逐步构造。"}</span></div></section>;
}

export function GrammarTreeWidget({ scene }){
 const cfg=cfgOf(scene); const nodes=cfg.nodes||[]; const roots=nodes.filter(n=>!n.parentId); const children=id=>nodes.filter(n=>n.parentId===id); const Node=({n,depth=0})=><li><div className="rounded-lg border border-black/10 p-3 dark:border-white/15" style={{marginLeft:`${Math.min(depth,4)*1.1}rem`}}><strong>{n.label}</strong>{n.role&&<span className="ml-2 text-xs opacity-60">{n.role}</span>}{n.explanation&&<p className="mt-1 text-sm opacity-75">{n.explanation}</p>}</div>{children(n.id).length?<ul className="mt-2 space-y-2">{children(n.id).map(c=><Node key={c.id} n={c} depth={depth+1}/>)}</ul>:null}</li>;
 return <section className={panel} data-modern-widget="grammar-tree-lab"><h3 className="font-semibold">{cfg.title || "语法树"}</h3><ul className="mt-4 space-y-2">{roots.map(n=><Node key={n.id} n={n}/>)}</ul>{cfg.boundary&&<p className="mt-3 text-xs opacity-65">{cfg.boundary}</p>}</section>;
}

export function SourceComparisonWidget({ scene }){
 const cfg=cfgOf(scene); const lenses=cfg.lenses||[]; const [lens,setLens]=useState(lenses[0]?.id||""); return <section className={panel} data-modern-widget="source-comparison-lab"><h3 className="font-semibold">来源比较</h3><p className="mt-2 text-sm/7">{cfg.prompt}</p><div className="mt-3 flex flex-wrap gap-2">{lenses.map(l=><button key={l.id} type="button" className={button} aria-pressed={lens===l.id} onClick={()=>setLens(l.id)}>{l.label}</button>)}</div><div className="mt-4 grid gap-3 md:grid-cols-2">{(cfg.sources||[]).map(s=><article key={s.id} className="rounded-lg border border-black/10 p-4 dark:border-white/15"><h4 className="font-semibold">{s.title}</h4><p className="mt-1 text-xs opacity-60">{[s.creator,s.date].filter(Boolean).join(" · ")}</p><p className="mt-3 text-sm/7">{s.excerpt}</p>{lens&&<p className="mt-3 text-sm"><strong>{lenses.find(l=>l.id===lens)?.label}：</strong>{s.analysis?.[lens]}</p>}</article>)}</div>{cfg.synthesisPrompt&&<p className="mt-4 text-sm"><strong>综合：</strong>{cfg.synthesisPrompt}</p>}</section>;
}

function GraphWidget({ scene, kind }){
 const cfg=cfgOf(scene); const nodes=cfg.nodes||[]; const edges=cfg.edges||[]; const byId=Object.fromEntries(nodes.map(n=>[n.id,n]));
 return <section className={panel} data-modern-widget={kind}><h3 className="font-semibold">{kind==="causal-dag-lab"?"因果 DAG":"论证图"}</h3><p className="mt-2 text-sm/7">{cfg.prompt || cfg.ariaLabel}</p><svg viewBox="0 0 760 400" className="mt-4 w-full rounded-xl border border-black/10 dark:border-white/10" role="img" aria-label={cfg.ariaLabel||cfg.prompt||"关系图"}>{edges.map((e,i)=>{const a=byId[e.from],b=byId[e.to]; if(!a||!b)return null; return <g key={i}><line x1={a.x} y1={a.y} x2={b.x} y2={b.y} stroke="currentColor" opacity=".45"/><text x={(a.x+b.x)/2} y={(a.y+b.y)/2-6} fontSize="12">{e.relation||"→"}</text></g>})}{nodes.map(n=><g key={n.id}><rect x={num(n.x)-80} y={num(n.y)-25} width="160" height="50" rx="12" fill="var(--ic-paper)" stroke="currentColor"/><text x={n.x} y={num(n.y)+5} textAnchor="middle" fontSize="13">{n.label}</text></g>)}</svg>{cfg.boundary&&<p className="mt-3 text-xs opacity-65">{cfg.boundary}</p>}{cfg.causalClaimBoundary&&<p className="mt-3 text-xs opacity-65">{cfg.causalClaimBoundary}</p>}</section>;
}
export function ArgumentMapWidget(props){ return <GraphWidget {...props} kind="argument-map-lab"/>; }
export function CausalDagWidget(props){ return <GraphWidget {...props} kind="causal-dag-lab"/>; }

export function EvidenceMatrixWidget({ scene }){
 const cfg=cfgOf(scene); return <section className={panel} data-modern-widget="evidence-matrix-lab"><h3 className="font-semibold">证据矩阵</h3><p className="mt-2 text-sm/7">{cfg.prompt}</p><div className="mt-4 overflow-x-auto"><table className="w-full border-collapse text-left text-sm"><thead><tr><th className="border-b p-2">证据</th><th className="border-b p-2">设计</th><th className="border-b p-2">可支持主张</th><th className="border-b p-2">限制</th></tr></thead><tbody>{(cfg.rows||[]).map(r=><tr key={r.id}><th className="border-b p-2 align-top">{r.label}</th><td className="border-b p-2 align-top">{r.design}</td><td className="border-b p-2 align-top">{r.claimScope}</td><td className="border-b p-2 align-top">{r.limitation}</td></tr>)}</tbody></table></div>{cfg.boundary&&<p className="mt-3 text-xs opacity-65">{cfg.boundary}</p>}</section>;
}

export function ProofPracticeWidget({ scene }){
 const cfg=cfgOf(scene); const steps=cfg.steps||[]; const [order,setOrder]=useState(steps.map(s=>s.id)); const move=(i,d)=>setOrder(xs=>{const n=[...xs],j=i+d;if(j<0||j>=n.length)return xs;[n[i],n[j]]=[n[j],n[i]];return n;}); const correct=JSON.stringify(order)===JSON.stringify(cfg.answer||[]);
 return <section className={panel} data-modern-widget="proof-practice"><h3 className="font-semibold">证明排序练习</h3><p className="mt-2 text-sm/7">{cfg.prompt}</p><ol className="mt-3 space-y-2">{order.map((id,i)=>{const s=steps.find(x=>x.id===id)||{};return <li key={id} className="rounded-lg border border-black/10 p-3 text-sm dark:border-white/15"><div>{s.text}</div><div className="mt-2 flex gap-2"><button className={button} onClick={()=>move(i,-1)}>↑</button><button className={button} onClick={()=>move(i,1)}>↓</button></div></li>})}</ol><p className="mt-3 text-sm">{correct?cfg.feedback?.correct:cfg.hint || cfg.feedback?.incorrect}</p></section>;
}

export const builtinWidgetRegistry = Object.freeze({
 "equation": EquationWidget,
 "process-animation": ProcessAnimationWidget,
 "motion-lab": MotionLabWidget,
 "simulation": SimulationWidget,
 "random-trial-lab": RandomTrialWidget,
 "fbd-lab": FbdWidget,
 "circuit-lab": CircuitWidget,
 "map-lab": MapWidget,
 "code": CodeTraceWidget,
 "stats-lab": StatsWidget,
 "data-lab": DataLabWidget,
 "genetics-lab": GeneticsWidget,
 "cloze-lab": ClozeWidget,
 "sentence-builder-lab": SentenceBuilderWidget,
 "grammar-tree-lab": GrammarTreeWidget,
 "source-comparison-lab": SourceComparisonWidget,
 "argument-map-lab": ArgumentMapWidget,
 "causal-dag-lab": CausalDagWidget,
 "evidence-matrix-lab": EvidenceMatrixWidget,
 "proof-practice": ProofPracticeWidget,
});
