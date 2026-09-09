#!/usr/bin/env python3
"""Machine guardrail for proposed reusable Skill changes."""
from __future__ import annotations
import argparse,json,posixpath,sys
from pathlib import Path,PurePosixPath

sys.dont_write_bytecode=True
SCHEMA='interactive-classroom-refinement-plan'
CLASSIFICATIONS={'course-local','pack-candidate','core-candidate'}
DECISIONS={'accept','reject','defer'}
OPS={'modify','add','delete','no-skill-change'}
PACKS={'mathematics','physics','chemistry','biology','computer-science','ml-ai','statistics','social-science','humanities','language','geography','procedural-vocational'}
CORE_PREFIXES=('SKILL.md','README.md','agents/openai.yaml','references/','discipline-packs/','assets/','scripts/','examples/')
PACK_PREFIXES=('references/widgets/','examples/regression/')

def safe_rel(path:str)->bool:
 if not isinstance(path,str) or not path or '\\' in path or path.startswith('/') or ':' in path.split('/')[0]:return False
 p=PurePosixPath(path)
 return '..' not in p.parts and '.' not in p.parts and posixpath.normpath(path)==path

def allowed_core(path): return path in {'SKILL.md','README.md','agents/openai.yaml'} or any(path.startswith(p) for p in CORE_PREFIXES if p.endswith('/'))
def allowed_pack(path,pack): return path.startswith(f'discipline-packs/{pack}/') or any(path.startswith(p) for p in PACK_PREFIXES)

def main()->int:
 ap=argparse.ArgumentParser();ap.add_argument('plan',type=Path);a=ap.parse_args();fails=[]
 try:d=json.loads(a.plan.read_text(encoding='utf-8'))
 except Exception as e:print('FAIL: invalid JSON:',e);return 1
 if d.get('schema')!=SCHEMA:fails.append(f'schema must be {SCHEMA}')
 classification=d.get('classification');decision=d.get('decision')
 if classification not in CLASSIFICATIONS:fails.append('classification must be course-local, pack-candidate, or core-candidate')
 if decision not in DECISIONS:fails.append('decision must be accept, reject, or defer')
 if d.get('dryRun') is not True:fails.append('dryRun must be true before applying reusable changes')
 pack=d.get('disciplinePack')
 if pack not in PACKS:fails.append('disciplinePack must be a canonical Pack id')
 changes=d.get('targetChanges')
 if not isinstance(changes,list) or not changes:fails.append('targetChanges must be a non-empty list')
 else:
  for i,ch in enumerate(changes):
   if not isinstance(ch,dict):fails.append(f'targetChanges[{i}] must be an object');continue
   op=ch.get('operation');path=ch.get('path')
   if op not in OPS:fails.append(f'targetChanges[{i}] has invalid operation')
   if op=='no-skill-change':
    if path not in (None,''):fails.append(f'targetChanges[{i}] no-skill-change must not name a reusable path')
    continue
   if not safe_rel(path):fails.append(f'targetChanges[{i}] has unsafe/non-relative path');continue
   if classification=='course-local':fails.append('course-local plans must use no-skill-change only')
   elif classification=='pack-candidate' and not allowed_pack(path,pack):fails.append(f'pack-candidate path outside Pack/widget/regression allowlist: {path}')
   elif classification=='core-candidate' and not allowed_core(path):fails.append(f'core-candidate path outside sibling Skill allowlist: {path}')
   if op=='delete' and d.get('explicitDeletionApproval') is not True:fails.append('delete requires explicitDeletionApproval=true')
 if classification in {'pack-candidate','core-candidate'} and decision=='accept':
  tests=d.get('regressionTests') or []
  if not isinstance(tests,list) or not tests or not all(isinstance(x,str) and x.strip() for x in tests):fails.append('accepted reusable change requires regressionTests')
 rationale=d.get('rationale')
 if not isinstance(rationale,str) or len(rationale.strip())<20:fails.append('rationale must be a substantive string')
 if fails:
  for x in fails:print('FAIL:',x)
  print(f'RESULT: FAIL ({len(fails)} failure(s))');return 1
 print('RESULT: PASS');return 0
if __name__=='__main__':raise SystemExit(main())
