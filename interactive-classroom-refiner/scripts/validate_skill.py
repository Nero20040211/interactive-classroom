#!/usr/bin/env python3
"""Static release gate for interactive-classroom-refiner.

The executable Refiner is release-number agnostic. A human-facing release
identifier is allowed only in README.md.
"""
from __future__ import annotations
import os,re,subprocess,sys
from pathlib import Path

sys.dont_write_bytecode=True
REQUIRED=[
 'SKILL.md','README.md','LICENSE.txt','agents/openai.yaml',
 'references/refinement-loop.md','references/refinement-policy.md',
 'scripts/validate_feedback_bundle.py','scripts/migrate_feedback_bundle.py','scripts/prepare_refinement_review.py',
 'scripts/validate_refinement_plan.py','scripts/validate_decision_log.py','scripts/test_refiner.py','scripts/validate_sibling_contract.py',
 'examples/sample-session-feedback.json','examples/sample-language-feedback.json','examples/sample-geometry-figure-feedback.json',
 'templates/refinement-plan.json','templates/decision-log.jsonl',
]

def main(root:Path)->int:
 root=root.resolve();fails=[]
 for rel in REQUIRED:
  if not (root/rel).is_file():fails.append('missing '+rel)
 skill=(root/'SKILL.md').read_text(encoding='utf-8') if (root/'SKILL.md').is_file() else ''
 for tok in ['interactive-classroom-refiner','three indicators','course-local','Pack candidate','core candidate','Animation-specific refinement','migrate_feedback_bundle.py','validate_refinement_plan.py','validate_decision_log.py','scripts/audit_animation_content_fit.py','scripts/run_regression.py','scripts/test_negative_gates.py','interactive-classroom-session-feedback']:
  if tok not in skill:fails.append('SKILL.md missing '+tok)
 loop=(root/'references/refinement-loop.md').read_text(encoding='utf-8') if (root/'references/refinement-loop.md').is_file() else ''
 for tok in ['validate_feedback_bundle.py','migrate_feedback_bundle.py','validate_refinement_plan.py','validate_decision_log.py']:
  if tok not in loop:fails.append(f'refinement-loop.md must reference {tok}')
 if 'GitHub textbook stress suite' in loop or 'stress-tests/github-textbooks' in loop:fails.append('refinement-loop.md references removed historical stress-suite paths')
 if (root/'templates/decision-log.jsonl').is_file() and not (root/'templates/decision-log.jsonl').read_text(encoding='utf-8').strip():fails.append('decision-log template must not be empty')
 release_marker=re.compile(r'\bv\d+(?:\.\d+)+\b');versioned_path=re.compile(r'(?:^|[-_])v\d+(?:[._-]\d+)+',re.I);text_suffixes={'.md','.py','.json','.yaml','.yml','.txt'}
 for path in root.rglob('*'):
  if versioned_path.search(path.name):fails.append(f'versioned path in formal Refiner: {path.relative_to(root)}')
  if not path.is_file() or path.name in {'README.md','validate_skill.py'} or path.suffix.lower() not in text_suffixes:continue
  text=path.read_text(encoding='utf-8',errors='replace');m=release_marker.search(text)
  if m:fails.append(f'release/history version marker outside README: {path.relative_to(root)} -> {m.group(0)}')
  if 'schemaVersion' in text:fails.append(f'schemaVersion must not drive Refiner behavior: {path.relative_to(root)}')
 forbidden_parts={'node_modules','dist','.build','.pytest_cache'}
 for path in root.rglob('*'):
  rel=path.relative_to(root)
  if any(part in forbidden_parts for part in rel.parts) or (path.is_file() and path.suffix in {'.map'}):fails.append(f'generated/build artifact in formal Refiner: {rel}')
 if not fails:
  env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'}
  for cmd,label in [([sys.executable,'scripts/test_refiner.py'],'Refiner E2E'),([sys.executable,'scripts/validate_decision_log.py','templates/decision-log.jsonl'],'decision-log template')]:
   proc=subprocess.run(cmd,cwd=root,capture_output=True,text=True,env=env)
   if proc.returncode:fails.append(label+' failed: '+((proc.stdout or '')+(proc.stderr or '')).strip().replace('\n',' | '))
   else:print(f'CHECK: {label}: PASS')
 if fails:
  for x in dict.fromkeys(fails):print('FAIL:',x)
  print(f'RESULT: FAIL ({len(set(fails))} failure(s))');return 1
 print('RESULT: PASS');return 0
if __name__=='__main__':raise SystemExit(main(Path(sys.argv[1]) if len(sys.argv)>1 else Path('.')))
