#!/usr/bin/env python3
"""Validate generalized, privacy-minimized refinement decision records."""
from __future__ import annotations
import argparse,json,sys
from pathlib import Path

sys.dont_write_bytecode=True
CLASSIFICATIONS={'course-local','pack-candidate','core-candidate'}
DECISIONS={'accepted','rejected','deferred','accept','reject','defer'}
FORBIDDEN_KEYS={'learnername','email','rawfeedback','rawlearnerfeedback','password','token','secret','accesstoken','apikey','api_key'}

def walk(o,path='record'):
 errors=[]
 if isinstance(o,dict):
  for k,v in o.items():
   if str(k).replace('-','').replace('_','').lower() in {x.replace('_','') for x in FORBIDDEN_KEYS}:errors.append(f'privacy-minimization violation at {path}.{k}')
   errors.extend(walk(v,f'{path}.{k}'))
 elif isinstance(o,list):
  for i,v in enumerate(o):errors.extend(walk(v,f'{path}[{i}]'))
 return errors

def main()->int:
 ap=argparse.ArgumentParser();ap.add_argument('log',type=Path);a=ap.parse_args();fails=[]
 lines=[x for x in a.log.read_text(encoding='utf-8').splitlines() if x.strip()]
 if not lines:fails.append('decision log must contain at least one JSONL record')
 for i,line in enumerate(lines,1):
  try:r=json.loads(line)
  except Exception as e:fails.append(f'line {i} invalid JSON: {e}');continue
  if r.get('classification') not in CLASSIFICATIONS:fails.append(f'line {i} invalid classification')
  if r.get('decision') not in DECISIONS:fails.append(f'line {i} invalid decision')
  if not isinstance(r.get('rationale'),str) or len(r.get('rationale','').strip())<20:fails.append(f'line {i} rationale too short')
  for key in ['testsAdded','evidence']:
   if not isinstance(r.get(key),list) or not all(isinstance(x,str) for x in r.get(key,[])):fails.append(f'line {i} {key} must be a string list')
  fails.extend(f'line {i}: {x}' for x in walk(r))
 if fails:
  for x in fails:print('FAIL:',x)
  print(f'RESULT: FAIL ({len(fails)} failure(s))');return 1
 print('RESULT: PASS');return 0
if __name__=='__main__':raise SystemExit(main())
