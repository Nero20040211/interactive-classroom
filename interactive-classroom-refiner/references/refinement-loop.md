# Learning → Skill refinement loop

`interactive-classroom-refiner` is an explicit, reviewable maintenance workflow for the sibling `interactive-classroom` Skill. The classroom teaches; this Skill changes the teaching system only after the user asks for iteration.

## Why not mutate the teaching Skill automatically?

A single learning session can contain learner misunderstandings, personal preferences, accidental clicks, incomplete notes, or factual corrections that are themselves wrong. Automatically writing these observations into the core would overfit the Skill and could propagate errors across disciplines.

## Runtime side: explicit session feedback only

The current teaching Skill may export a local JSON file with schema:

`interactive-classroom-session-feedback`

Current version-neutral `interactive-classroom-refinement-bundle` files may also be read for explicit/manual refinement workflows. Legacy versioned feedback schemas must first be converted with `scripts/migrate_feedback_bundle.py`; the strict validator never branches on legacy version numbers.

The learner-facing HTML must not:

- collect hidden clickstream analytics;
- call network endpoints;
- silently persist or upload data;
- infer sensitive learner attributes;
- edit Skill or Pack files directly.

## Refiner side: controlled pipeline

When feedback or stress-test evidence is supplied, run this sequence:

1. **Migrate when needed** — `python scripts/migrate_feedback_bundle.py <legacy.json> --out <current.json>`, then **validate** with `python scripts/validate_feedback_bundle.py <feedback.json>`.
2. **Prepare review** — `python scripts/prepare_refinement_review.py <feedback.json> --out <review.md>` when a structured review sheet is useful.
3. **Reproduce** bugs and learning failures where possible.
4. **Audit the three indicators** on the affected course: explanation suitability, principle-revealing animation, gap-revealing practice.
5. **Classify** each observation:
   - `course-local`;
   - `Pack candidate`;
   - `core candidate`.
6. **Check evidence**. Learner experience is strong evidence about pedagogy, not automatic evidence that source content is factually wrong.
7. **Draft the smallest reusable change as a refinement plan** and run `python scripts/validate_refinement_plan.py <plan.json>`. Reusable plans require `dryRun=true` and must stay inside the target allowlist. Prefer course repair over Pack change, and Pack change over core change.
8. **Regression-test**:
   - course-local: validate the revised course;
   - Pack change: add/strengthen a positive fixture and destructive negative test;
   - core change: rerun the sibling `scripts/run_regression.py`, `scripts/test_negative_gates.py`, and the full sibling `scripts/validate_skill.py` release gate.
9. **Record the generalized decision** in JSONL and run `python scripts/validate_decision_log.py <decision-log.jsonl>`, never retaining unnecessary personal learner details or secrets.

## Promotion rules

A candidate may be promoted to a Pack rule when at least one of these is true:

- the defect is objectively reproducible in the Pack runtime/validator;
- the rule follows a stable subject convention verified against trusted references;
- the same pedagogical failure appears in multiple independent fixtures/sessions;
- the user explicitly requests a Pack-level behavior and it survives Pack regressions.

A candidate may be promoted to core only if it is discipline-agnostic and survives cross-Pack regression.

## Positive feedback matters

`worked-well` and `figure-helpful` observations may also improve the Skill. Preserve a reviewed, generalized teaching pattern and its regression test; do not retain raw personal feedback in the Skill corpus unless the user explicitly requests it and it is necessary.


## Animation evidence
Treat `animation-content-mismatch`, `animation-too-fast`, `animation-misleading`, and `animation-helpful` as explicit evidence. Inspect primitives, conceptual entity bindings, semantic step logic, timing, and misleading-risk boundaries.
