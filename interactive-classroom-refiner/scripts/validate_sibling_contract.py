#!/usr/bin/env python3
"""Check the explicit feedback/refinement contract against a sibling teaching Skill."""
from __future__ import annotations

import sys
from pathlib import Path

SCHEMA='interactive-classroom-session-feedback'


def main(refiner: Path, teaching: Path | None = None) -> int:
    refiner=refiner.resolve()
    teaching=(teaching or (refiner.parent/'interactive-classroom')).resolve()
    fails=[]
    required=[
        teaching/'SKILL.md',
        teaching/'assets/classroom-shell.html',
        teaching/'assets/modern-runtime/src/App.jsx',
        teaching/'scripts/run_regression.py',
        teaching/'scripts/test_modern_runtime.py',
        teaching/'scripts/test_negative_gates.py',
        teaching/'scripts/audit_animation_content_fit.py',
        teaching/'scripts/validate_skill.py',
        refiner/'scripts/migrate_feedback_bundle.py',
        refiner/'scripts/validate_refinement_plan.py',
        refiner/'scripts/validate_decision_log.py',
    ]
    for path in required:
        if not path.is_file(): fails.append(f'missing sibling file: {path}')
    validator=refiner/'scripts/validate_feedback_bundle.py'
    if validator.is_file() and SCHEMA not in validator.read_text(encoding='utf-8'): fails.append('Refiner validator does not accept current session feedback schema')
    for rel in ['assets/classroom-shell.html','assets/modern-runtime/src/App.jsx']:
        path=teaching/rel
        if path.is_file():
            text=path.read_text(encoding='utf-8',errors='replace')
            if SCHEMA not in text: fails.append(f'{rel} does not export current session feedback schema')
            if 'automaticSkillChange:false' not in text: fails.append(f'{rel} must explicitly prohibit automatic Skill mutation')
    if fails:
        for x in fails: print('FAIL:',x)
        print(f'RESULT: FAIL ({len(fails)} failure(s))'); return 1
    print('RESULT: PASS'); return 0


if __name__=='__main__':
    root=Path(sys.argv[1]) if len(sys.argv)>1 else Path(__file__).resolve().parents[1]
    sibling=Path(sys.argv[2]) if len(sys.argv)>2 else None
    raise SystemExit(main(root,sibling))
