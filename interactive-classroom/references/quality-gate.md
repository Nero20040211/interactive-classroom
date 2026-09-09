# Quality Gate

A classroom is ready only when applicable items pass.

## Learning/domain design
- [ ] A topic-only request can be completed without asking the user to select internal modes/widgets.
- [ ] Every substantial concept/discussion/interactive/PBL scene contains explicit learner-visible knowledge explanation.
- [ ] Interaction applies/deepens taught knowledge rather than replacing it.
- [ ] Objectives are observable and mapped to scenes/assessment.
- [ ] Discipline Router profile is explicit for substantial courses.
- [ ] A Discipline Specialist pass checks notation, units and domain conventions.
- [ ] Important misconceptions have targeted remediation.
- [ ] Evidence, inference, illustration, synthetic data and simulation are distinguished.
- [ ] No invented empirical data/parameters/clinical facts are presented as sourced.

## Outline → scene architecture
- [ ] Stage/Scene outline existed before final HTML generation.
- [ ] Each interactive scene has one justified `widgetType`.
- [ ] Only the relevant widget contract was used.
- [ ] Stable IDs exist for stage/scene/objective/widget elements.

## Interactive widgets
- [ ] Simulation shows units, assumptions and guided experiment.
- [ ] 3D-like visualization has rotate/reset/select and text fallback.
- [ ] Game has finite rules, transparent scoring and debrief.
- [ ] Code widget does not falsely claim execution.
- [ ] Diagram relation semantics are visible; drag has keyboard alternative.
- [ ] Procedural skill shows order/checkpoints and safety limits where relevant.
- [ ] Equation steps expose notation/reasons/assumptions.
- [ ] Data lab states provenance/units and does not imply causality from description alone.

## Teacher Action Bus
- [ ] Every declared action type is implemented by the target widget.
- [ ] Teacher narration matches actual visible widget changes.
- [ ] Guidance can be advanced manually and replayed/reset.
- [ ] No fake “AI thinking” behavior.

## Assessment
- [ ] Deterministic kinds use transparent rules.
- [ ] Numeric items state tolerance/units where relevant.
- [ ] Free-form prose uses self-rubric, not fake AI grading.
- [ ] Mastery includes transfer/application when required.

## PBL/procedural
- [ ] Role, mission, resources, decisions/microtasks and milestones are explicit.
- [ ] Consequences/checkpoints are deterministic and inspectable.
- [ ] Safety-critical practice is not presented as certification.

## HTML/runtime
- [ ] Knowledge explanation is visually primary and readable without interacting with controls.
- [ ] Raw internal scene/widget enum names are not the dominant learner-facing labels.
- [ ] Layout looks like a learning studio rather than a dense dashboard.
- [ ] meta + app markers present.
- [ ] Opens directly from disk.
- [ ] No network/model endpoints/external scripts/styles/fonts.
- [ ] `aria-live`, keyboard focus and reduced motion work.
- [ ] No broken placeholders or learner-facing NaN/undefined/Infinity.
- [ ] Strict validator passes.

## Cross-disciplinary release check
At least one tested scene/fixture covers each broad family:
- [ ] formal/quantitative;
- [ ] physical/experimental or life science;
- [ ] computational/data;
- [ ] social/interpretive/language;
- [ ] procedural/vocational.

## reader/depth gate

- [ ] Ordinary “learn/study/teach me” requests use `learn-deep` unless the user requests a short overview.
- [ ] Major concepts contain enough prose/reasoning to stand alone; no “summary + three bullets” treatment of a difficult concept.
- [ ] At least one worked example/evidence chain is present for each difficult central concept.
- [ ] Current-page TOC reflects knowledge subsections on wide screens.
- [ ] Clicking a graph node, revealing dialogue, submitting an answer or showing a hint preserves vertical scroll position.
- [ ] Previous/next navigation lands at the new scene heading instead of document top.
- [ ] Dragging a knowledge node updates SVG in place without scene re-render.
- [ ] Visual style is textbook/documentation-first, not dashboard-first.


## mathematical presentation

- [ ] Major formulas use native MathML Core, not code/monospace blocks.
- [ ] Every display formula has TeX/spoken fallback and nearby prose explanation.
- [ ] Derivation steps expose reasons and do not skip nontrivial transformations.
- [ ] Symbols, assumptions and domains are defined before assessment.


## textbook semantics

- [ ] Formal named claims use stable semantic IDs and, for systematic courses, stable numbering/labels.
- [ ] A central theorem/lemma/proposition has a linked proof, proof sketch, justification, or explicit proof omission reason.
- [ ] Proof steps expose non-trivial inference reasons and use structured MathML for substantive formulas.
- [ ] Worked examples show reasoning rather than only final answers.
- [ ] Exercises depend on already-taught knowledge and offer a useful hint/solution/self-check path.
- [ ] Semantic cross references resolve to valid block IDs.
- [ ] The right-side page outline highlights the subsection currently being read.
- [ ] Header page position is labeled as course/navigation progress, not mastery.


## release gate

- [ ] `course.sources` IDs are unique and every citation resolves.
- [ ] `sourcePolicy: grounded` scenes each include at least one visible citation.
- [ ] Auto-numbered semantic blocks/formulas have stable IDs; cross references resolve to semantic blocks or formulas.
- [ ] Proof Practice has deterministic step/reason keys and teaches the proof before testing it.
- [ ] Physics/engineering quantity scenes declare units and dimensions when dimensional analysis is used.
- [ ] Structured chemistry reactions preserve compound identity and, when marked balanced, pass atom-count conservation.
- [ ] Search works without re-rendering the current scene; session bookmarks are labeled as session-only behavior.
- [ ] Bundled seven-subject regression suite passes strict validation with zero warnings.

### Formula, animation, and experiment checks

- No substantive mathematical equality/inequality leaks into ordinary narrative strings.
- Every declared formula slot is MathML + TeX/spoken fallback.
- If a diagram declares animation, it has at least two deterministic reveal steps, manual controls, and reduced-motion support.
- If `experimentPolicy=adjustable-when-applicable`, quantitative practice widgets expose learner-adjustable variables when a deterministic model is available.
- Slider/parameter input updates must not re-render the whole page or reset scroll position.
- Physics, biology, chemistry, machine learning, artificial intelligence, geography, and computer-science regression fixtures must all pass strict validation with zero warnings.


## Discipline Pack release gate
- [ ] `meta.disciplinePack` is declared for substantial courses and matches the topic.
- [ ] Only the primary pack plus at most two justified secondary packs are loaded.
- [ ] Pack-native widgets satisfy their subject-specific validator gates.
- [ ] Mathematics geometry labs use fixed coordinate bounds and measurable quantities.
- [ ] Physics FBD labs separate forces from velocity/motion arrows; circuit labs declare source and ideal-model assumptions.
- [ ] Chemistry molecule labs declare atom/bond structure and model disclaimer.
- [ ] Biology genetics labs declare allowed genotypes and phenotype mapping.
- [ ] Statistics labs state the distribution model and interpretation target.
- [ ] ML/AI boundary/search labs label synthetic data/trace assumptions.
- [ ] Map labs contain embedded verified data plus provenance; no invented real boundaries.

## figure and practice gate

For geometry-native Mathematics courses:
- core inventory figures resolve by stable ID;
- every core item has representation-building plus disambiguation figure coverage;
- figures have a stated learning purpose/caption and do not claim metric accuracy by appearance.

For mastery-loop courses with the relevant flags:
- examples include a standard case plus contrast/boundary/misconception case;
- practice references actually cover guided, independent and transfer/retrieval levels;
- two-novel-transfer mastery rules require at least two correct items per objective.

## learner-first additions

- [ ] learner HTML does not expose source-coverage/debug/internal-schema/Pack/validator/refinement jargon;
- [ ] anything called animation has real object/state change, not only node reveal or moving arrows;
- [ ] staged diagrams are labeled as step-by-step diagrams;
- [ ] process animation has pause/step/replay and reduced-motion behavior;
- [ ] adjustable experiments expose a meaningful learner-controlled variable and model-relevant result.
