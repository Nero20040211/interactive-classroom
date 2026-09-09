#!/usr/bin/env python3
"""Migrate legacy versioned feedback exports into the stable version-neutral schema."""
from __future__ import annotations
import argparse, json, re, sys
from datetime import datetime, timezone
from pathlib import Path

sys.dont_write_bytecode = True
CURRENT_SESSION='interactive-classroom-session-feedback'
CURRENT_REFINEMENT='interactive-classroom-refinement-bundle'
LEGACY=re.compile(r'^(interactive-classroom-(?:session-feedback|refinement-bundle))/\d+(?:\.\d+)*$')

def iso_now(): return datetime.now(timezone.utc).isoformat().replace('+00:00','Z')

def main()->int:
 ap=argparse.ArgumentParser();ap.add_argument('input',type=Path);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
 try:d=json.loads(a.input.read_text(encoding='utf-8'))
 except Exception as e: print('FAIL: invalid JSON:',e);return 1
 schema=d.get('schema')
 m=LEGACY.match(str(schema or ''))
 if m: d['schema']=m.group(1)
 elif schema not in {CURRENT_SESSION,CURRENT_REFINEMENT}: print('FAIL: unsupported legacy/current schema');return 1
 exported=d.get('exportedAt') or iso_now(); d['exportedAt']=exported
 policy=d.setdefault('policy',{})
 if 'autoMutation' in policy and 'automaticSkillChange' not in policy: policy['automaticSkillChange']=policy.pop('autoMutation')
 policy['automaticSkillChange']=False; policy['telemetry']='explicit-user-entered-only'
 d['explicitUserExport']=True
 course=d.setdefault('course',{}); primary=course.get('disciplinePack'); secondary=course.get('secondaryPacks') or []
 course['secondaryPacks']=[x for i,x in enumerate(secondary) if isinstance(x,str) and x!=primary and x not in secondary[:i]]
 for obs in d.get('observations') or []:
  if not isinstance(obs,dict): continue
  obs.setdefault('recordedAt',exported)
  obs['objectiveIds']=[str(x) for i,x in enumerate(obs.get('objectiveIds') or []) if str(x).strip() and str(x) not in [str(y) for y in (obs.get('objectiveIds') or [])[:i]]]
  obs['types']=[str(x) for i,x in enumerate(obs.get('types') or []) if str(x).strip() and str(x) not in [str(y) for y in (obs.get('types') or [])[:i]]]
  obs.setdefault('scopeHint','unknown')
 a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8');print(a.out);return 0
if __name__=='__main__':raise SystemExit(main())
