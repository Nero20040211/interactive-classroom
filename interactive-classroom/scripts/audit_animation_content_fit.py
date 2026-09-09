#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,sys
from pathlib import Path

PROFILE_PRIMITIVES={
 'mathematics-probability':{'die','coin','sample-point','math-point','vector'},
 'mathematics-dynamic-quantity':{'math-point','vector'},
 'mathematics-geometry':{'math-point','vector'},
 'statistics-probability':{'die','coin','sample-point','math-point','vector'},
 'statistics-sampling':{'coin','die','sample-point','math-point','vector'},
 'physics-motion':{'vector'},
 'physics-force':{'vector'},
 'physics-field':{'vector'},
 'physics-wave':{'vector'},
 'biology-cellular-process':{'molecule','energy-token','water-drop','cell'},
 'biology-genetics':{'molecule','energy-token','cell'},
 'biology-system':{'molecule','energy-token','cell'},
 'chemistry-reaction':{'molecule','ion','electron','energy-token','vector'},
 'chemistry-particle':{'molecule','ion','electron','energy-token','vector'},
 'chemistry-electrochemistry':{'molecule','ion','electron','energy-token','vector'},
 'computer-science-runtime':{'stack-frame','array-cell','pointer'},
 'computer-science-algorithm':{'stack-frame','array-cell','pointer'},
 'computer-science-data-structure':{'stack-frame','array-cell','pointer'},
 'geography-earth-system':{'water-drop','air-mass','plate','vector'},
 'geography-flow':{'water-drop','air-mass','plate','vector'},
 'geography-spatial-change':{'water-drop','air-mass','plate','vector'},
 'geography-water-cycle':{'water-drop','air-mass','plate','vector'},
 'ml-ai-optimization':{'math-point','vector','array-cell','pointer'},
 'ml-ai-search':{'math-point','vector','array-cell','pointer'},
 'ml-ai-decision':{'math-point','vector','array-cell','pointer'},
}

def profile_primitives(pack,profile):
 p=str(profile or '')
 for prefix,types in PROFILE_PRIMITIVES.items():
  if p==prefix or p.startswith(prefix+'-'): return types
 return set()

def extract(p:Path):
 t=p.read_text(encoding='utf-8',errors='replace')
 if p.suffix.lower()=='.json': return json.loads(t)
 marker='const course='; i=t.find(marker)
 if i<0: raise ValueError('cannot find embedded course JSON')
 value,_=json.JSONDecoder().raw_decode(t[i+len(marker):].lstrip())
 if not isinstance(value,dict): raise ValueError('course JSON is not an object')
 return value

def main():
 ap=argparse.ArgumentParser(); ap.add_argument('course',type=Path); ap.add_argument('--json',action='store_true'); a=ap.parse_args()
 d=extract(a.course); meta=d.get('meta') or {}; pol=meta.get('animationContentPolicy') or {}; pack=meta.get('disciplinePack'); fails=[]; checked=0
 for sc in d.get('scenes',[]):
  c=sc.get('content') or {}
  if c.get('widgetType')!='process-animation': continue
  checked+=1; sid=sc.get('id','?'); cfg=c.get('widgetConfig') or {}; sem=cfg.get('animationSemantics') or {}; steps=cfg.get('steps') or []; actors=cfg.get('actors') or []
  for k in ['profile','knowledgeType','teachingGoal','corePrinciple','entities','stateVariables','stepLogic','mustNotMislead','motionRationale','contentFitAudit']:
   if not sem.get(k): fails.append(sid+':missing-'+k)
  if pack and not str(sem.get('profile','')).startswith(pack+'-'): fails.append(sid+':profile-pack-mismatch')
  if sem.get('knowledgeType')=='static-relation': fails.append(sid+':animation-not-needed')
  ids={str(x.get('id')) for x in actors if isinstance(x,dict) and x.get('id')}
  bound=set()
  for e in sem.get('entities') or []:
   if not isinstance(e,dict) or not e.get('concept'): fails.append(sid+':entity-concept')
   for aid in (e.get('actorIds') or []):
    bound.add(str(aid))
    if str(aid) not in ids: fails.append(sid+':entity-unknown-'+str(aid))
  meaningful={str(x.get('id')) for x in actors if isinstance(x,dict) and x.get('type') not in {'track','line','secant-line','text','zone'} and x.get('id')}
  if not meaningful.issubset(bound): fails.append(sid+':unbound-knowledge-actor')
  relation_types={'passes-through','touches','contains','enters','attached-to','points-to'}
  amap={str(x.get('id')):x for x in actors if isinstance(x,dict) and x.get('id')}
  for rel in sem.get('semanticRelations') or []:
   if not isinstance(rel,dict) or rel.get('type') not in relation_types: fails.append(sid+':semantic-relation-type'); continue
   src=str(rel.get('source','')); tgts=[str(x) for x in (rel.get('targets') or [])]
   if src not in ids or not tgts or any(x not in ids for x in tgts): fails.append(sid+':semantic-relation-ref'); continue
   scoped=[str(x) for x in (rel.get('whenSteps') or [])]
   valid_actions={str(x.get('semanticAction','')) for x in steps if isinstance(x,dict) and x.get('semanticAction')}
   if scoped and (not all(scoped) or any(x not in valid_actions for x in scoped)): fails.append(sid+':semantic-relation-step-scope')
   stype=(amap.get(src) or {}).get('type')
   if rel.get('type')=='passes-through' and stype not in {'line','secant-line','track','vector'}: fails.append(sid+':semantic-relation-passes-through-source')
   if rel.get('type')=='contains' and stype!='zone': fails.append(sid+':semantic-relation-contains-source')
   if rel.get('type')=='points-to' and stype not in {'pointer','vector'}: fails.append(sid+':semantic-relation-points-to-source')
  if any(x.get('type') not in {'track','line','secant-line','text','zone'} and not x.get('semanticRole') for x in actors if isinstance(x,dict)): fails.append(sid+':semantic-role')
  if len(sem.get('stepLogic') or [])!=len(steps): fails.append(sid+':stepLogic')
  if any(not x.get('semanticAction') or not x.get('whyItMatters') for x in steps): fails.append(sid+':step-explanation')
  if pol.get('requireKeyStep') and not any(x.get('emphasis')=='key' for x in steps): fails.append(sid+':key-step')
  preferred=profile_primitives(pack,sem.get('profile'))
  if pol.get('requireDomainPrimitiveWhenAvailable') and preferred and not ({x.get('type') for x in actors if isinstance(x,dict)} & preferred): fails.append(sid+':profile-generic-only')
  audit=sem.get('contentFitAudit') or {}
  if audit.get('entitySpecificity') not in {'high','medium'}: fails.append(sid+':entity-specificity')
  if audit.get('motionNaturalness') not in {'high','medium'}: fails.append(sid+':motion-naturalness')
  if audit.get('misleadingRisk') not in {'low','controlled'}: fails.append(sid+':misleading-risk')
  if not audit.get('visualStory'): fails.append(sid+':visual-story')
 out={'course':meta.get('title') or meta.get('id'),'pack':pack,'checked':checked,'failures':fails,'pass':not fails}
 if a.json: print(json.dumps(out,ensure_ascii=False,indent=2))
 else: print(('PASS' if not fails else 'FAIL')+': animation content fit '+json.dumps(out,ensure_ascii=False))
 return 0 if not fails else 1
if __name__=='__main__': sys.exit(main())
