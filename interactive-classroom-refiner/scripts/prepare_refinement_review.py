#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,subprocess,sys
from pathlib import Path

def main()->int:
 ap=argparse.ArgumentParser(); ap.add_argument('bundle',type=Path); ap.add_argument('--out',type=Path); args=ap.parse_args()
 validator=Path(__file__).with_name('validate_feedback_bundle.py')
 r=subprocess.run([sys.executable,str(validator),str(args.bundle)],capture_output=True,text=True)
 if r.returncode:
  print(r.stdout+r.stderr); return r.returncode
 d=json.loads(args.bundle.read_text(encoding='utf-8')); pack=(d.get('course') or {}).get('disciplinePack','unknown')
 lines=[f'# Refinement review — {pack}','',f'Course: {(d.get("course") or {}).get("title","")}','','> Classification is a review decision, not an automatic consequence of scopeHint or rating.','']
 for i,o in enumerate(d.get('observations') or [],1):
  lines += [f'## Observation {i}',f'- Scene: `{o.get("sceneId")}` — {o.get("sceneTitle","")}',f'- Types: {", ".join(o.get("types") or []) or "none"}',f'- Rating: {o.get("rating")}',f'- Scope hint: {o.get("scopeHint","unknown")}',f'- Learner note: {o.get("note","")}', '', '- Classification: `course-local | pack-candidate | core-candidate`','- Decision: `accept | reject | defer`','- Reproduction / evidence:','- Smallest justified change:','- Regression tests to add/run:','- Generalized decision record (do not copy unnecessary personal details):','']
 text='\n'.join(lines)
 out=args.out or args.bundle.with_suffix('.review.md'); out.write_text(text,encoding='utf-8'); print(out); return 0
if __name__=='__main__':sys.exit(main())
