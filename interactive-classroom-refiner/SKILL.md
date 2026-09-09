---
name: interactive-classroom-refiner
description: Review explicit learner feedback and regression evidence to iteratively improve the sibling interactive-classroom Skill. Use only when the user explicitly asks to optimize, refine, iterate, repair, or feed learning experience back into interactive-classroom. Accept current session-feedback JSON, migrated/manual refinement bundles, plain-language feedback, course HTML/JSON, and regression/audit reports. Never mutate the teaching Skill from a classroom session without an explicit user request.
---

# Interactive Classroom Refiner

This Skill is deliberately separate from `interactive-classroom`. The teaching Skill teaches; this Skill changes the teaching system.

## Explicit invocation boundary

Use this Skill only after the user asks to iterate/improve the Skill, for example:

- “用这次学习反馈优化 interactive-classroom”
- “把这些问题反哺到 Skill”
- “根据这门课的压力测试迭代 Pack”

Do not run because a learner merely answered incorrectly or left feedback in the HTML.

## Inputs

Accept any combination of:

1. `interactive-classroom-session-feedback` exported by current classrooms;
2. current `interactive-classroom-refinement-bundle` from manual workflows; legacy versioned bundles must first pass `scripts/migrate_feedback_bundle.py`;
3. plain-language learner feedback;
4. generated course JSON/HTML;
5. three-indicator audit reports;
6. sibling cross-disciplinary regression, negative-gate, and audit reports.

## Refinement pipeline

1. **Normalize and validate** the supplied evidence. Legacy versioned JSON goes through `scripts/migrate_feedback_bundle.py` before the strict current validator.
2. **Reproduce** claimed bugs or learning failures where possible.
3. **Audit the three indicators**: explanation suitability, principle-revealing animation, gap-revealing practice.
4. **Classify scope**:
   - course-local;
   - Pack candidate;
   - core candidate.
5. **Check source truth separately from learner experience**. Learner confusion is strong evidence about pedagogy, not automatic evidence that source content is false.
6. **Draft a machine-checkable refinement plan** and run `scripts/validate_refinement_plan.py`. Course-local plans must declare no reusable Skill change; Pack/core targets must stay inside their allowlists and reusable changes require `dryRun=true`.
7. **Make the smallest reusable change**. Prefer course repair over Pack change; Pack over core. Deletion requires explicit approval.
8. **Add a positive regression and a destructive negative test** for every reusable rule.
9. **Run sibling cross-disciplinary regressions and destructive negative gates** for Pack/core changes, plus the affected pedagogical/animation audits and the sibling release gate.
10. **Record a concise generalized decision** and validate the JSONL with `scripts/validate_decision_log.py`; do not store raw personal learner details or secrets.

## Promotion rule

A single learner preference should not become a global rule. Pack/core promotion needs at least one of: reproducible failure, authoritative subject convention, repeated independent evidence, or an explicit user-requested behavior that survives regression.

## Sibling Skill discovery

Prefer a sibling directory named `../interactive-classroom`. If the user supplies another path, use that. Never silently edit unrelated Skills.

## Regression evidence in the sibling Skill

The teaching Skill keeps its current self-contained evidence under `examples/regression/` and exposes `scripts/run_regression.py`, `scripts/test_negative_gates.py`, `scripts/audit_three_indicators.py`, and `scripts/audit_animation_content_fit.py`. For Pack/core changes, strengthen the affected fixture or add a new one, add a destructive negative test when the rule is machine-checkable, and rerun the sibling release gate. Do not rely on removed historical stress-suite directories.

## Animation-specific refinement

Classify animation feedback as content/object mismatch, motion mismatch, pacing, missing explanation, misleading visual model, or helpful animation. Reproduce the scene and run the sibling `scripts/audit_animation_content_fit.py`; promote to a Pack profile only when the pattern is reusable.
