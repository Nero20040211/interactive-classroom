# Mastery Practice Loop

This loop combines the strongest reusable ideas from several public teaching skills while preserving Interactive Classroom's offline runtime boundary.

## External design ideas absorbed

### SuperTutor
Reference: https://github.com/cskwork/supertutor-skill

Absorb:
- every core concept must have a plain explanation plus a concrete worked example;
- the learner must generate an explanation, not merely recognize one;
- fix the **first** gap rather than dumping many questions at once;
- use progressive hints before revealing an answer;
- mastery claims come from an independent deterministic gate, not the teaching voice.

Adaptation here:
- HTML `explain-back` is reflective and does not pretend to auto-grade free text;
- `commonGaps` maps six useful gap types to one repair question each;
- objective mastery is certified only by a deterministic `masteryGate` using keyed questions;
- `scripts/validate_mastery_gate.py` is intentionally separate from the normal HTML validator.

### OpenMAIC
Reference: https://github.com/THU-MAIC/OpenMAIC

Absorb:
- outline → scene generation;
- typed interactive widgets;
- teacher actions that can direct attention/state;
- multi-role classroom and PBL.

Adaptation here:
- generation uses Codex; runtime remains one offline HTML file;
- no server-side model, API key, database, or live hidden teacher is implied.

### codex-teacher-skill
Reference: https://github.com/sekiwhat/codex-teacher-skill

Absorb:
- inventory the source before authoring the lesson;
- explicitly cover definitions, formulas, theorems, examples, proofs, code and important conclusions;
- reader-first HTML and strong math validation.

Adaptation here:
- `contentInventory` + `sourceCoverage` make coverage machine-checkable;
- missing pages/sections must be declared rather than silently filled from memory.

### Teacher Skill / related subject tutors
Reference example: https://github.com/BTHawake/Teacher_skill

Absorb selectively:
- deliberate practice;
- cumulative retrieval / spaced review concepts;
- subject-specific teaching strategies.

Adaptation here:
- requires cumulative retrieval inside a course;
- multi-day persistence remains opt-in only and is not required for strict offline classrooms.

## Canonical learning loop

For a core concept:

1. **Elicit / Predict** — expose the learner's current model.
2. **Explain deeply** — prerequisite → intuition → precise statement → mechanism/proof.
3. **Worked examples (>=2 for mastery-loop courses)** — use contrasting examples when useful.
4. **Guided practice** — hints available; one conceptual step at a time.
5. **Independent practice** — no answer leakage.
6. **Transfer challenge** — vary surface features/context while preserving the target principle.
7. **Explain-back** — learner restates from memory; self-check against required ideas.
8. **First-gap repair** — select one gap and answer one Socratic repair question.
9. **Cumulative retrieval** — mix current and earlier objectives.
10. **Independent Mastery Gate** — deterministic objective-by-objective check.
11. **Session feedback** — optionally export what worked/failed for later explicit review by the separate refiner Skill.

## Six explain-back gap types

Recommended canonical IDs:

- `causal-chain` — steps are named but why/how connections are missing;
- `circular-definition` — explanation merely repeats the term;
- `undefined-jargon` — essential term is used without unpacking it;
- `missing-boundary` — no conditions, limits, or counterexample boundary;
- `missing-example` — explanation cannot instantiate the idea concretely;
- `broken-analogy` — analogy is treated as the mechanism or breaks at a critical point.

The page must not auto-assign a gap from free text. The learner may choose the first observed gap, or a generation-time tutor may pre-author a repair path.

## Practice ladder

Questions may declare `practiceLevel`:

- `guided`
- `independent`
- `transfer`
- `retrieval`

A mastery-loop course should avoid three nearly identical substitutions. Prefer:

- one near-transfer item after the worked example;
- one independent item with reduced scaffolding;
- one far/novel transfer item;
- later cumulative retrieval that interleaves prior objectives.

## Deterministic mastery gate

A `mastery` scene can include:

```json
{
 "masteryGate": {
 "threshold": 0.8,
 "objectiveRules": [
 {"objectiveId":"O1","questionIds":["m1","m2"],"minCorrect":2}
 ]
 }
}
```

Rules:
- every course objective must have a rule;
- at least two keyed questions per objective;
- overall threshold and every objective rule must pass;
- free-response explain-back does **not** count as deterministic certification;
- failing the gate should route the learner to targeted remediation, not merely display a red score.

## representation gate

When a concept is likely to fail because the learner cannot yet form the right spatial/structural representation, insert a pedagogical figure **before** expecting transfer. The sequence becomes:

**explain → show what to notice → worked example → guided practice → independent practice → transfer → explain-back → mastery**.

A figure is not evidence of mastery. It is scaffolding that should make the later independent task possible.
