# Animation Content-Fit Contract 

Animation is a knowledge representation, not decoration. Before generating motion, classify the learning target as `mechanism-process`, `dynamic-quantity`, `structure-build`, `reasoning-evolution`, `simulation-experiment`, or `static-relation`. Static relations should normally use a pedagogical figure or native lab rather than cinematic movement.

## Required `animationSemantics`

For content-fit `process-animation`, declare `profile`, `knowledgeType`, `teachingGoal`, `corePrinciple`, conceptual `entities` bound to actor IDs, `stateVariables`, one-to-one `stepLogic`, `mustNotMislead`, `motionRationale`, and a `contentFitAudit`. Visible actors need `semanticRole`; every step needs `semanticAction`, `whyItMatters`, `emphasis`, and a concrete observation/change description. At least one step must be a slower `key` step.

## Domain-native primitives

- mathematics/statistics: `die`, `coin`, `sample-point`, `math-point`, `vector`;
- physics: `projectile`, `projection-marker`, `vector`;
- biology: `molecule`, `energy-token`, `cell`;
- chemistry: `molecule`, `ion`, `electron`, `vector`;
- computer science: `stack-frame`, `array-cell`, `pointer`;
- geography: `water-drop`, `air-mass`, `plate`, `vector`.

Prefer a native lab when it exposes state more truthfully than animation (for example recursion/search/proof). Never use generic moving boxes merely to make a page feel dynamic.

## Misleading-risk examples

- projectile motion without drag must not visually decay horizontal velocity;
- sample-space membership motion is a set-classification metaphor, not a chronological causal process;
- biochemical animations must preserve molecule/count structure such as carbon bookkeeping;
- algorithm animation must respect execution order and invariants;
- geography flow arrows must encode a process/direction/scale relation, not decoration.


## Semantic contact / containment

Do not treat every overlap as a visual defect. When contact is mathematically or scientifically meaningful, declare `animationSemantics.semanticRelations`. Supported relations are `passes-through`, `touches`, `contains`, `enters`, `attached-to`, and `points-to`. Examples: a secant line passes through P and Q; an electron enters an acceptor; a pointer touches the array cell it points at; a water drop enters a cloud/river region. The validator permits overlap only for declared relations and still rejects unrelated collisions. Use optional `whenSteps` with semantic-action names to scope a relation to only the steps where contact is conceptually valid; an unscoped relation applies throughout the animation.
