# 数学 / 逻辑 Discipline Pack

Pack ID: `mathematics`

Status: **validated-native**

Preferred: equation, proof-practice, geometry-lab, solid-geometry-lab, space-geometry-lab. Use Definition/Lemma/Theorem/Proof when natural. Geometry labs must declare coordinate bounds and at least one measurable invariant. Do not replace proof with animation.

## Pack quality gate

- Knowledge explanation remains primary.
- Use only subject-native notation and declare assumptions.
- Prefer a native lab when manipulation materially improves understanding; otherwise use prose/diagram.
- Core offline, accessibility, MathML and citation contracts still apply.


## geometry teaching: diagrams + labs + proof

Use `solid-geometry-lab` for deterministic parameter experiments involving common solids. Use `space-geometry-lab` when the learning objective is to distinguish spatial line/plane relations. Diagrams are explanatory projections; positional claims must come from named model objects/theorems, never from pixel appearance.

For mastery-loop mathematics courses, use at least two worked examples for each core concept, then guided → independent → transfer practice and an explain-back before final mastery.


### Pedagogical figure heuristics

For geometry, solid geometry, projection and spatial-relation topics, plan explanation figures **before** compiling the HTML. Prefer:

- `concept` for object structure;
- `step` for projection/construction;
- `reasoning` for proof scaffolds such as bridge lines;
- `compare` / `misconception` for cases where a 2D drawing can mislead.

A core geometry concept should normally have at least two complementary figures when `figurePolicy.mode="geometry-native"`. Every figure must be schematic-honest: state what it encodes and what metric/spatial claims cannot be inferred from pixels.

For deep textbook learning, combine figures with 2+ worked examples (standard plus contrast/boundary), guided → independent → transfer/retrieval practice, explain-back, and an objective-by-objective mastery gate.

## Probability native guidance 

Use static pedagogical figures for event/set distinctions, `process-animation` for a trial or independence mechanism unfolding in time, and `random-trial-lab` for frequency stability/random simulation. Keep probability identities in structured MathML.


## animation profile

Prefer mathematically meaningful motion (probability outcomes, moving points, geometric transforms). Do not animate proofs just to make them move.
