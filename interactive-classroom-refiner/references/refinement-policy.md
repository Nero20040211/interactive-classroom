# Refinement policy

## Safety / integrity invariants

- No silent auto-mutation from classroom HTML.
- No hidden telemetry.
- No automatic promotion of user claims to factual truth.
- No learner-specific details stored in the Skill regression corpus unless intentionally anonymized and necessary.
- No Pack/core change without a reproducible rationale and regression coverage.

## Decision levels

### Course-local
Accept when it improves the current lesson without changing reusable subject rules.

Examples: add a counterexample, expand an explanation, fix one citation, repair a scene-specific control.

### Pack-candidate
Use when the issue is subject-generalizable.

Examples: physics force arrows need interaction sources; language cloze needs accepted variants; humanities paraphrases need explicit text status; social-science causal diagrams need a causal-assumption boundary.

### Core-candidate
Use only for generic infrastructure.

Examples: scroll jumps, broken keyboard navigation, MathML fallback, session feedback export, offline boundary.

## Decision log shape

```json
{
  "bundleId": "...",
  "observationIndex": 0,
  "classification": "pack-candidate",
  "decision": "accepted",
  "target": "discipline-packs/language",
  "rationale": "...",
  "testsAdded": ["..."],
  "evidence": ["..."]
}
```


## Pedagogical-figure feedback

The explicit learner feedback bundle may include `figure-helpful` or `figure-confusing-or-missing`. Use these to refine figure heuristics only after review. Do not preserve raw personal feedback in the Pack; preserve the reviewed, generalizable teaching rule and its regression test.


## Animation-specific evidence

When feedback concerns an animation, classify it separately as `animation-content-mismatch`, `animation-motion-mismatch`, `animation-too-fast`, `animation-missing-explanation`, `animation-misleading`, or `animation-helpful`. Reproduce the affected scene and run the sibling content-fit audit before promoting a change. A single preference about color or motion is course-local unless it exposes a reusable accessibility or domain-mechanism rule.


## Machine guardrails

Before applying a reusable change, create a plan shaped like `templates/refinement-plan.json` and run `scripts/validate_refinement_plan.py`. Course-local evidence may only produce `no-skill-change`; Pack candidates may touch the selected Pack, widget contracts, and regression fixtures; core candidates remain inside the sibling Interactive Classroom allowlist. Path traversal and unrelated sibling Skills are forbidden. Deletes require explicit approval.

Decision logs are generalized maintenance evidence, not raw learner archives. Run `scripts/validate_decision_log.py` and exclude raw learner text, identity fields, credentials, tokens, or other secrets.
