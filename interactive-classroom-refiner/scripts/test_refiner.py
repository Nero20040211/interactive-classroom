#!/usr/bin/env python3
from __future__ import annotations
import json, os, subprocess, sys, tempfile
from pathlib import Path

sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[1]; PY=sys.executable; ENV={**os.environ,'PYTHONDONTWRITEBYTECODE':'1','PYTHONIOENCODING':'utf-8'}
VALID=ROOT/'examples/sample-session-feedback.json'; VALIDATOR=ROOT/'scripts/validate_feedback_bundle.py'; PREP=ROOT/'scripts/prepare_refinement_review.py'; MIGRATE=ROOT/'scripts/migrate_feedback_bundle.py'; PLANVAL=ROOT/'scripts/validate_refinement_plan.py'; LOGVAL=ROOT/'scripts/validate_decision_log.py'

def run(args,expect=0,needle=None):
 p=subprocess.run(args,capture_output=True,text=True,encoding='utf-8',errors='replace',env=ENV);out=(p.stdout or '')+(p.stderr or '')
 if p.returncode!=expect or (needle and needle not in out):
  print(out);raise SystemExit(f'command returned {p.returncode}, expected {expect}, needle={needle}: {args}')
 return p

run([PY,str(VALIDATOR),str(VALID)])
with tempfile.TemporaryDirectory(prefix='ic-refiner-') as td_raw:
 td=Path(td_raw);out=td/'review.md';run([PY,str(PREP),str(VALID),'--out',str(out)])
 txt=out.read_text(encoding='utf-8')
 for token in ['Classification','Decision','Smallest justified change','Regression tests']:
  if token not in txt:raise SystemExit(f'review output missing {token}')
 base=json.loads(VALID.read_text(encoding='utf-8'))
 def bad_case(name,mutate,needle):
  d=json.loads(json.dumps(base));mutate(d);p=td/f'{name}.json';p.write_text(json.dumps(d,ensure_ascii=False),encoding='utf-8');run([PY,str(VALIDATOR),str(p)],expect=1,needle=needle)
 bad_case('auto-mutation',lambda d:d['policy'].__setitem__('automaticSkillChange',True),'automaticSkillChange must be false')
 bad_case('bool-rating',lambda d:d['observations'][0].__setitem__('rating',True),'rating must be a finite number')
 bad_case('duplicate-types',lambda d:d['observations'][0].__setitem__('types',['worked-well','worked-well']),'invalid or duplicate types')
 bad_case('invalid-secondary',lambda d:d['course'].__setitem__('secondaryPacks',['not-a-pack']),'secondaryPacks')
 bad_case('missing-recorded',lambda d:d['observations'][0].pop('recordedAt',None),'recordedAt')
 legacy=json.loads(json.dumps(base));legacy['schema']='interactive-classroom-session-feedback/1';legacy['observations'][0].pop('recordedAt',None);legacy_path=td/'legacy.json';legacy_path.write_text(json.dumps(legacy,ensure_ascii=False),encoding='utf-8')
 run([PY,str(VALIDATOR),str(legacy_path)],expect=1,needle='migrate legacy schemas first');migrated=td/'migrated.json';run([PY,str(MIGRATE),str(legacy_path),'--out',str(migrated)]);run([PY,str(VALIDATOR),str(migrated)])
 # Refinement plan guardrails.
 good=json.loads((ROOT/'templates/refinement-plan.json').read_text(encoding='utf-8'));goodp=td/'plan.json';goodp.write_text(json.dumps(good,ensure_ascii=False),encoding='utf-8');run([PY,str(PLANVAL),str(goodp)])
 def plan_bad(name,mutate,needle):
  d=json.loads(json.dumps(good));mutate(d);p=td/f'plan-{name}.json';p.write_text(json.dumps(d,ensure_ascii=False),encoding='utf-8');run([PY,str(PLANVAL),str(p)],expect=1,needle=needle)
 plan_bad('traversal',lambda d:d['targetChanges'][0].__setitem__('path','../other-skill/SKILL.md'),'unsafe/non-relative path')
 plan_bad('pack-core',lambda d:d['targetChanges'][0].__setitem__('path','scripts/validate_skill.py'),'pack-candidate path outside')
 plan_bad('course-local',lambda d:(d.__setitem__('classification','course-local'),d['targetChanges'][0].__setitem__('path','SKILL.md')),'course-local plans must use no-skill-change only')
 plan_bad('delete',lambda d:(d['targetChanges'][0].__setitem__('operation','delete'),d.__setitem__('explicitDeletionApproval',False)),'explicitDeletionApproval=true')
 run([PY,str(LOGVAL),str(ROOT/'templates/decision-log.jsonl')])
 badlog=td/'bad-log.jsonl';badlog.write_text(json.dumps({'classification':'core-candidate','decision':'accepted','rationale':'This generalized record is intentionally long enough to validate but includes nested secret data.','testsAdded':[],'evidence':[],'meta':{'secret':'do-not-store'}},ensure_ascii=False)+'\n',encoding='utf-8');run([PY,str(LOGVAL),str(badlog)],expect=1,needle='privacy-minimization')
print('REFINER E2E: PASS')
