#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,re,sys
from pathlib import Path

def extract(path:Path):
    txt=path.read_text(encoding='utf-8',errors='replace')
    if path.suffix.lower()=='.json': return json.loads(txt)
    marker='const course='
    i=txt.find(marker)
    if i<0: raise ValueError('cannot find embedded course JSON')
    payload=txt[i+len(marker):].lstrip()
    try:
        value,_=json.JSONDecoder().raw_decode(payload)
    except json.JSONDecodeError as e:
        raise ValueError(f'cannot decode embedded course JSON: {e}') from e
    if not isinstance(value,dict): raise ValueError('embedded course data is not an object')
    return value

def content(sc): return sc.get('content') or {}
def knowledge(sc): return sc.get('knowledge') or content(sc).get('knowledge') or {}
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('course',type=Path); ap.add_argument('--json',action='store_true'); a=ap.parse_args()
    d=extract(a.course); meta=d.get('meta') or {}; policy=meta.get('learnerQualityPolicy') or {}
    core=[s for s in d.get('scenes',[]) if s.get('type') in {'concept','interactive','discussion','pbl'} and s.get('objectiveIds')]
    ex_fail=[]
    for s in core:
        k=knowledge(s); sid=s.get('id','?')
        has_example=bool(k.get('workedExamples') or [b for b in k.get('semanticBlocks',[]) if (b.get('kind') or b.get('type') or '').lower() in {'example','exercise'}])
        if not k.get('mentalModel') or not has_example or not (k.get('boundaries') or k.get('pitfalls')): ex_fail.append(sid)
    explanation={'pass':not ex_fail,'failScenes':ex_fail,'checkedScenes':len(core)}
    proc=[s for s in d.get('scenes',[]) if content(s).get('widgetType')=='process-animation']
    an_fail=[]
    fit_policy=meta.get('animationContentPolicy') or {}
    fit_fail=[]
    domain={'die','coin','sample-point','math-point','molecule','energy-token','projectile','projection-marker','vector','ion','electron','stack-frame','array-cell','pointer','water-drop','air-mass','plate'}
    for s in proc:
        cfg=content(s).get('widgetConfig') or {}; steps=cfg.get('steps') or []; sid=s.get('id','?')
        if not cfg.get('principle') or not cfg.get('principleCheck') or len(steps)<3 or any(not x.get('focus') or not x.get('changeSummary') for x in steps): an_fail.append(sid)
        if fit_policy.get('mode')=='content-fit':
            sem=cfg.get('animationSemantics') or {}; actors=cfg.get('actors') or []
            needed=['profile','knowledgeType','teachingGoal','corePrinciple','entities','stateVariables','stepLogic','mustNotMislead','motionRationale','contentFitAudit']
            bad=any(not sem.get(k) for k in needed) or len(sem.get('stepLogic') or [])!=len(steps)
            bad=bad or any(not x.get('semanticAction') or not x.get('whyItMatters') for x in steps)
            if fit_policy.get('requireKeyStep') and not any(x.get('emphasis')=='key' for x in steps): bad=True
            if fit_policy.get('requireDomainPrimitiveWhenAvailable') and actors and not any(x.get('type') in domain for x in actors): bad=True
            audit=sem.get('contentFitAudit') or {}
            if audit.get('misleadingRisk') not in {'low','controlled'}: bad=True
            if bad: fit_fail.append(sid)
    animation={'pass':not an_fail and not fit_fail,'failScenes':an_fail,'contentFitFailScenes':fit_fail,'checkedScenes':len(proc),'notRequired':len(proc)==0}
    q=[]
    for s in d.get('scenes',[]):
        for item in ((content(s).get('items') or []) + (content(s).get('questions') or [])): q.append((s,item))
    gaps_by_obj={}
    pr_fail=[]
    for s,item in q:
        oids=item.get('objectiveIds') or ([item.get('objectiveId')] if item.get('objectiveId') else (s.get('objectiveIds') or [])); oid=oids[0] if oids else None; tags=item.get('gapTags') or ([] if not item.get('diagnosticTag') else [item.get('diagnosticTag')])
        if oid: gaps_by_obj.setdefault(oid,set()).update(tags)
        if policy.get('requireDiagnosticGapTags') and not tags: pr_fail.append(item.get('id','?'))
    core_oids={o.get('id') for o in d.get('objectives',[]) if o.get('id')}
    shallow=[oid for oid in core_oids if len(gaps_by_obj.get(oid,set()))<2] if policy.get('requireDiagnosticGapTags') else []
    practice={'pass':not pr_fail and not shallow,'untaggedItems':pr_fail,'objectivesWithFewGapTypes':shallow,'checkedItems':len(q)}
    out={'course':meta.get('title') or meta.get('id'),'explanationSuitability':explanation,'principleAnimation':animation,'gapRevealingPractice':practice,'overallPass':explanation['pass'] and animation['pass'] and practice['pass']}
    if a.json: print(json.dumps(out,ensure_ascii=False,indent=2))
    else:
        print('THREE-INDICATOR AUDIT')
        for name,key in [('Explanation suitability','explanationSuitability'),('Principle-revealing animation','principleAnimation'),('Gap-revealing practice','gapRevealingPractice')]: print(('PASS' if out[key]['pass'] else 'FAIL')+': '+name+' '+json.dumps(out[key],ensure_ascii=False))
        print('RESULT:', 'PASS' if out['overallPass'] else 'FAIL')
    return 0 if out['overallPass'] else 1
if __name__=='__main__': sys.exit(main())
