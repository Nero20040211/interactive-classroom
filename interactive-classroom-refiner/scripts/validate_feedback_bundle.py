#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,math,sys
from datetime import datetime
from pathlib import Path

sys.dont_write_bytecode=True
SCHEMAS={'interactive-classroom-session-feedback','interactive-classroom-refinement-bundle'}
TYPES={'unclear-explanation','missing-example','incorrect-content','interaction-friction','math-or-notation','pacing-or-depth','source-question','worked-well','figure-helpful','figure-confusing-or-missing','animation-content-mismatch','animation-motion-mismatch','animation-too-fast','animation-missing-explanation','animation-misleading','animation-helpful'}
SCOPES={'unknown','course','pack','core'}
PACKS={'mathematics','physics','chemistry','biology','computer-science','ml-ai','statistics','social-science','humanities','language','geography','procedural-vocational'}

def iso_ok(v):
 if not isinstance(v,str) or not v.strip(): return False
 try: datetime.fromisoformat(v.replace('Z','+00:00')); return True
 except ValueError: return False

def unique_strings(v,max_items=100): return isinstance(v,list) and len(v)<=max_items and all(isinstance(x,str) and x.strip() for x in v) and len(v)==len(set(v))

def main()->int:
 ap=argparse.ArgumentParser();ap.add_argument('bundle',type=Path);a=ap.parse_args();fails=[]
 if a.bundle.stat().st_size>2_000_000: fails.append('feedback bundle must be <=2 MB')
 try:d=json.loads(a.bundle.read_text(encoding='utf-8'))
 except Exception as e: print('FAIL: invalid JSON:',e);return 1
 if d.get('schema') not in SCHEMAS:fails.append('schema must be stable interactive-classroom-session-feedback or interactive-classroom-refinement-bundle; migrate legacy schemas first')
 if d.get('explicitUserExport') is not True:fails.append('explicitUserExport must be true')
 if not iso_ok(d.get('exportedAt')):fails.append('exportedAt must be an ISO-8601 timestamp')
 policy=d.get('policy') or {}
 if policy.get('automaticSkillChange') is not False:fails.append('policy.automaticSkillChange must be false')
 if policy.get('telemetry')!='explicit-user-entered-only':fails.append('policy.telemetry must be explicit-user-entered-only')
 course=d.get('course') or {};pack=course.get('disciplinePack')
 if not isinstance(course.get('title'),str) or not course.get('title','').strip():fails.append('course.title must be a non-empty string')
 if course.get('courseId') is not None and not isinstance(course.get('courseId'),str):fails.append('course.courseId must be string or null')
 if pack not in PACKS:fails.append('course.disciplinePack must be a canonical Pack id')
 secondary=course.get('secondaryPacks') or []
 if not unique_strings(secondary,20) or any(x not in PACKS for x in secondary):fails.append('course.secondaryPacks must be a unique list of canonical Pack ids')
 if pack in secondary:fails.append('course.secondaryPacks must not repeat the primary Pack')
 obs=d.get('observations')
 if not isinstance(obs,list) or not obs:fails.append('observations must be a non-empty list')
 elif len(obs)>100:fails.append('observations must contain at most 100 entries')
 else:
  for i,o in enumerate(obs):
   if not isinstance(o,dict):fails.append(f'observation {i} is not an object');continue
   if o.get('sceneId') is not None and not isinstance(o.get('sceneId'),str):fails.append(f'observation {i} sceneId must be string or null')
   if not isinstance(o.get('sceneTitle',''),str) or len(o.get('sceneTitle',''))>500:fails.append(f'observation {i} sceneTitle must be <=500 chars')
   if not unique_strings(o.get('objectiveIds') or [],50):fails.append(f'observation {i} objectiveIds must be a unique string list')
   types=o.get('types') or []
   if not unique_strings(types,20) or any(x not in TYPES for x in types):fails.append(f'observation {i} contains invalid or duplicate types')
   rating=o.get('rating')
   if rating is not None and (type(rating) not in (int,float) or not math.isfinite(rating) or not 1<=rating<=5):fails.append(f'observation {i} rating must be a finite number 1..5 or null')
   if o.get('scopeHint','unknown') not in SCOPES:fails.append(f'observation {i} has invalid scopeHint')
   note=o.get('note','')
   if not isinstance(note,str) or len(note)>5000:fails.append(f'observation {i} note must be <=5000 chars')
   if not iso_ok(o.get('recordedAt')):fails.append(f'observation {i} recordedAt must be an ISO-8601 timestamp')
   if not types and rating is None and not note.strip():fails.append(f'observation {i} is empty')
 if fails:
  for x in fails:print('FAIL:',x)
  print(f'RESULT: FAIL ({len(fails)} failure(s))');return 1
 print('RESULT: PASS');return 0
if __name__=='__main__':raise SystemExit(main())
