---
name: interactive-classroom
description: Automatically turn broad learning intents into OpenMAIC-aligned, cross-disciplinary offline interactive classrooms in Codex without a separate LLM API key or deployed web service. Use automatically when the user says they want to learn, study, understand, review, practice, or be taught a topic (for example “我要学习密码学”, “教我微积分”, “带我系统学 Python”), especially when a structured or interactive learning experience would help. Treat explicit depth/polish teaching requests such as “我需要一个详细讲解…课程”, “精细讲解…”, “深入讲解…”, “详尽讲解…”, “高质量讲解…”, or English equivalents such as “detailed course”, “in-depth explanation”, and “thorough interactive course” as a strong natural-language trigger for the Modern Runtime unless the user explicitly asks for portable/zero-build output or the modern build toolchain is unavailable. Do not require $interactive-classroom or ic-build for ordinary learning requests. Infer the discipline, level, objectives, scene/widget mix, assessments, and offline HTML output unless the user specifies them. Every core learning scene must teach the knowledge explicitly before or alongside interaction. Do not force a classroom for a narrow one-off factual question unless the user asks for structured learning. The browser runtime must remain deterministic and offline unless the user explicitly requests a model connection.
---

# Interactive Classroom

Create a visual interactive classroom using **Codex as generation/revision-time intelligence** and an **offline browser artifact as runtime**. Use the portable single-file renderer or the optional React/Tailwind/Motion component renderer according to frontend complexity. Both profiles share one stable Stage/Scene learning model and the same knowledge-first pedagogy. Skill mutation/review remains delegated to the sibling `interactive-classroom-refiner` Skill.

## Runtime architecture

- **Portable renderer:** `assets/classroom-shell.html`, zero-build and direct `file://`.
- **Modern renderer:** `modern-react`, authored with pinned React/Tailwind/Motion + esbuild and compiled at generation time into one offline HTML artifact.
- **Animation contract:** portable and Modern share the optional `process-animation` fields; the renderer owns timing and the discipline adapter owns primitives/models.
- **Runtime routing:** read `references/frontend-runtime.md`; natural-language depth intent is a first-class Modern Runtime trigger, then complexity/environment rules apply.
- **Course model:** use the stable Stage/Scene schema independently of renderer choice.
- **Validation:** validate declared capabilities and learning contracts directly; never branch on a Skill or schema release number.

## Zero-config natural-language invocation

The normal entry point is **the learner's intent, not a mode name**. If the user says only:

- “我要学习密码学”
- “教我线性代数”
- “我想系统学习 Python”
- “带我复习世界史”
- “帮我理解量子力学”

activate this skill and internally treat the request as `ic-learn`. Do **not** ask the user to repeat the request using `$interactive-classroom`, `ic-build`, widget names, discipline labels, or validator flags.

`ic-learn` is an internal zero-config route:

1. infer the topic scope and a reasonable learner level;
2. run the Discipline Router;
3. build prerequisites, objectives and misconception map;
4. create a compact Stage/Scene outline;
5. choose only the widget types that improve the target concepts;
6. generate **knowledge-first** scenes;
7. add practice/assessment only after the relevant knowledge has been taught;
8. compile and validate one polished offline HTML classroom.

If the topic is broad and no level is given, default to a **foundation → intermediate** path, state the assumed scope in the orientation scene, and continue without clarification. Ask only when a missing constraint would make the result unsafe or materially wrong.

### Natural-language Modern Runtime fast path

Before doing the normal complexity routing, inspect the learner's wording. Treat a **teaching/course request plus an explicit depth or polish signal** as a strong request for the Modern Runtime. Typical signals include:

- Chinese: `详细讲解`, `详细的讲解`, `详细地讲解`, `详细课程`, `精细讲解`, `精讲`, `细致的讲解`, `详尽的讲解`, `深入地讲解`, `深度解析`, `全面讲解`, `系统详细讲解`, `高质量讲解`, `高质量课程`, `交互式详细讲解`, `可视化精讲`;
- English: `detailed course`, `detailed explanation`, `in-depth explanation`, `deep dive course`, `thorough explanation`, `fine-grained explanation`, `comprehensive interactive course`, `rich interactive explanation`.

Examples that should route directly to `modern-react` when the toolchain is available:

- “我需要一个详细讲解高中物理平抛运动的课程”或“我需要一个详细的讲解物理抛物线运动的课程”
- “请精细讲解二分查找，并做成交互课程”
- “给我一个深入讲解细胞呼吸的可视化课程”
- “I want a detailed interactive course on linear algebra.”

This is a **runtime preference trigger, not a pedagogy shortcut**: the course must still satisfy every knowledge-first, source, math, assessment, accessibility and animation-content-fit rule. Explicit learner constraints have higher priority: `不要/别用 React`, `不使用任何框架`, `原生 HTML/CSS/JS`, `vanilla JS`, `framework-free`, `portable`, `zero-build`, `single HTML` and equivalent wording force the portable path. Do not interpret the ordinary physics/topic word `motion` as a request for the Motion library unless the learner explicitly names the library/runtime or says to use it. If the modern build toolchain is unavailable, fall back to portable and state the fallback once instead of silently pretending Modern was built.

For deterministic prompt routing in maintenance/tests, `python scripts/select_runtime.py "<learner request>"` implements the same fast-path policy. A result of `auto` means continue with the normal complexity router.

Modes remain available for expert control, but they are optional.

## Non-negotiable runtime boundary

1. **Generation/revision — Codex:** reason, ground sources, plan stages/scenes, author course data/components, and compile the selected renderer. Generation-time Node/npm is allowed for the modern profile.
2. **Runtime — browser:** the delivered artifact runs local deterministic state, assessment/simulation, HTML/SVG/Canvas/WebGL as appropriate, and embedded assets. React/Motion may be bundled locally; Tailwind is compiled to CSS.
3. **No fake live AI:** pre-generated roles may guide the learner, but the offline page must not imply that a live LLM is running.
4. **No learner-runtime network by default:** no `fetch`, XHR, WebSocket, EventSource, remote scripts/styles/fonts, analytics, or model endpoints. A generation-time dependency install does not change this rule.
5. **Framework-neutral learning model:** Stage/Scene/course semantics must not depend on React component state. The same authored learning model remains inspectable/validatable independently of the renderer.

## Frontend runtime router

Read `references/frontend-runtime.md` before compiling. Apply routing in this order:

1. **Explicit portable override** — `portable`, `zero-build`, `single HTML`, `不要/别用 React`, `不使用任何框架`, `原生 HTML/CSS/JS`, `vanilla JS`, or equivalent wording → `portable`.
2. **Explicit modern-stack request** — React/Tailwind/Motion/component architecture → `modern-react`.
3. **Natural-language depth trigger** — detailed / 精细 / 深入 / 详尽 / 高质量 teaching-course intent as defined above → `modern-react`.
4. **Complexity router** — use `modern-react` for reusable component state, synchronized views, complex gestures/visualizations, or a large imperative renderer branch; otherwise use `portable`.
5. **Environment fallback** — if the optional modern toolchain is unavailable, fall back to `portable` and disclose the fallback once.

The modern profile uses pinned local dependencies and bundles them into the final HTML. Prefer `m` + `LazyMotion` over a full Motion surface by default, compile Tailwind classes at build time, keep class variants statically discoverable, wrap complex widgets in learner-safe error boundaries, and preserve the same local learning-feedback export used by the Refiner workflow. Core teaching scenes and the bundled regression widget surface must use the built-in Modern contract; course-specific widgets extend `generatedWidgetRegistry` explicitly and must be declared in `widget-manifest.json`.

## Discipline Packs — discipline-native routing

The core Skill delegates subject conventions to **Discipline Packs** under `discipline-packs/`. After the general Discipline Router identifies a subject family, load the matching `PACK.md` before choosing widgets. A pack defines: (1) notation/content conventions, (2) preferred/forbidden widgets, (3) subject-specific quality gates, and (4) regression expectations.

Canonical pack IDs:

- `mathematics` — equation, proof-practice, geometry-lab, solid-geometry-lab, space-geometry-lab, plus source-grounded pedagogical figures for geometry;
- `physics` — quantity-lab, motion-lab, fbd-lab, circuit-lab;
- `chemistry` — chemistry, molecule-lab;
- `biology` — animated diagram, annotation, genetics-lab;
- `computer-science` — code, diagram, procedural-skill;
- `ml-ai` — data-lab, ml-boundary-lab, search-tree-lab, proof-practice;
- `statistics` — data-lab, stats-lab;
- `social-science` — causal-dag-lab, evidence-matrix-lab, discussion, data-lab, PBL;
- `humanities` — source-comparison-lab, argument-map-lab, annotation, timeline, discussion;
- `language` — cloze-lab, sentence-builder-lab, grammar-tree-lab, annotation/dialogue; never claim live pronunciation scoring without a real speech engine;
- `geography` — diagram/data-lab and `map-lab` only with embedded verified geographic data; never invent boundaries;
- `procedural-vocational` — procedural-skill, PBL, checkpoint/safety contracts.

For substantial courses, write `meta.disciplinePack`. If a topic crosses families, select one primary pack and at most two secondary packs. Do not load every pack. Read `references/discipline-packs.md` and `references/discipline-pack-maturity.md`.

### Discipline-native widgets

- `geometry-lab` — draggable points/segments, invariant measurements and coordinate geometry;
- `fbd-lab` — learner-constructed free-body diagrams with explicit candidate forces and deterministic checking;
- `circuit-lab` — adjustable DC series/parallel circuits with voltage/current/resistance recalculation;
- `molecule-lab` — offline rotatable atom/bond structure with chemistry labels and geometry notes;
- `genetics-lab` — Punnett-square inheritance experiments with adjustable parent genotypes;
- `stats-lab` — distribution/threshold explorer with adjustable parameters and deterministic probability readouts;
- `search-tree-lab` — explicit OPEN/CLOSED/current-node algorithm trace;
- `ml-boundary-lab` — adjustable linear decision boundary with live classification/accuracy;
- `map-lab` — embedded-data geographic viewer; requires provenance and verified coordinates/polygons.
- `solid-geometry-lab` — adjustable common-solid volume/surface experiments for the Mathematics Pack.
- `space-geometry-lab` — cuboid-based 3D line/plane relation reasoning for the Mathematics Pack.
- `cloze-lab` — context-sensitive gap completion with deterministic accepted answers and strategy feedback;
- `sentence-builder-lab` — token-level sentence construction with explicit target/accepted orders;
- `grammar-tree-lab` — clickable syntax/constituency structure with role explanations;
- `source-comparison-lab` — source-aware comparative reading across perspective, context and evidence lenses;
- `argument-map-lab` — claim/evidence/objection/qualification relations with source-aware evidence nodes;
- `causal-dag-lab` — causal assumptions, confounders and adjustment-set reasoning;
- `evidence-matrix-lab` — compare study designs, claim scope and limitations without overstating causality.

These widgets are not generic decoration. Use them only through the corresponding pack unless a second pack explicitly justifies them.


## Pedagogical figures + verifiable practice progression

For substantial or source-based learning, read `references/pedagogical-figures.md` and `references/practice-progression.md` in addition to the mastery-loop references. The goal is to close the gap between “the prose is complete” and “the learner can actually form the right representation and transfer it.”

### Explanation figures are first-class teaching objects

Core knowledge may include `knowledge.pedagogicalFigures`. A pedagogical figure is **not decoration** and does not replace prose, proof, examples or practice. It must have a stable `id`, `figureKind`, `title`, `learningPurpose`, `caption`, and a supported Pack template. Place it inside the explanation flow using `after` (for example `mentalModel`, `mechanism`, `section:<id>`, `examples`, `pitfalls`).

When a worked example depends on a spatial, mechanical, structural, or process representation, bind a direct offline figure with `workedExamples[].figureRef` and set the matching `visualNeed`. Modern and portable place that figure inside the example next to its steps and conclusion. Prefer a direct pedagogical figure over a text-only example or a mind-map-like diagram; direct means an implemented local SVG/template, never a remote image URL.

Canonical figure kinds:

- `concept` — build the first correct mental representation;
- `compare` — place confusable cases side by side;
- `step` — externalize a construction/procedure;
- `reasoning` — show why a proof/causal move is useful;
- `misconception` — contrast a tempting visual inference with the real condition.

For Mathematics geometry courses with `meta.figurePolicy.mode="geometry-native"`, strict validation requires `contentInventory[].figureRefs`, a minimum figure count per core item, and complementary figure kinds. Prefer simple SVG teaching diagrams with labels and captions over decorative imagery. Do not claim metric accuracy for schematic drawings.

For broader courses that should use this preference, set `meta.figurePolicy.mode="direct-first"`, `preferDirectFigures:true`, and an appropriate `maxMindMapLikeDiagrams` (normally `1`). A mind-map-like `diagram` is allowed only when its `visualPurpose` is a hierarchy/network/taxonomy/dependency/state-machine/argument structure and it has a `mindMapJustification`; additional instances beyond the cap need their own justification.

### Examples and practice are checked for diversity, not only count

For `meta.practicePolicy.mode="mastery-loop"`, the mastery policy can additionally enforce:

- `requireExampleContrast:true` — core inventory must include a `standard` worked example and at least one `contrast | boundary | misconception | reverse` example;
- `requirePracticeProgression:true` — referenced practice must cover `guided`, `independent`, and at least one `transfer | retrieval`;
- `requireTwoNovelTransfers:true` — each objective's mastery rule must require at least two `novelTransfer:true` items and `minCorrect >= 2`.

This is intentionally stricter than “more questions.” Five near-identical substitutions are worse than a smaller ladder that changes representation and removes scaffolding.

### Figure feedback remains learner feedback

The learner feedback UI may record `figure-helpful` and `figure-confusing-or-missing`. The main Skill only exports these observations. Promotion into reusable teaching rules belongs to the sibling `interactive-classroom-refiner` Skill and requires review plus regression evidence.

## Mastery-practice loop

For source-based or substantial learning, read `references/mastery-practice-loop.md`, `references/practice-foundations.md`, and `references/source-coverage-inventory.md`. The goal is to prevent “the page explained it, therefore the learner mastered it.”

A mastery-loop course should:

1. inventory the actual source before authoring (`sourceCoverage` + `contentInventory`);
2. give every core concept at least two concrete worked examples by default;
3. follow with guided → independent → transfer practice rather than repeated substitution;
4. use progressive `hintLadder` hints;
5. add an `explain-back` scene so the learner reconstructs the idea from memory;
6. let the learner identify the **first** explanation gap and answer one Socratic repair question;
7. interleave earlier objectives in cumulative retrieval;
8. end with a deterministic `masteryGate` that the teaching voice cannot self-approve;
9. run `scripts/validate_mastery_gate.py` independently after the normal HTML validator.

The `explain-back` runtime is intentionally honest: it does not claim to understand or AI-grade free text. It reveals required ideas and gap rubrics for self-diagnosis; objective mastery comes from keyed assessment.

For `meta.practicePolicy.mode="mastery-loop"`, strict validation checks the declared example/practice counts, source coverage, explain-back coverage, cumulative retrieval, and objective-by-objective mastery rules.

### Mathematics extensions

The Mathematics Pack adds:

- `solid-geometry-lab` — adjustable prism/pyramid/cylinder/cone/sphere/frustum models with deterministic area/volume outputs;
- `space-geometry-lab` — cuboid-based line/plane relation practice that distinguishes parallel/intersecting/skew/contained relations by model rules rather than apparent drawing angle.

## Session feedback boundary

The main Skill may expose a learner-visible **学习反馈** control and export a local `interactive-classroom-session-feedback` JSON file. This is only a record of explicitly entered learner observations. The main Skill does **not** classify feedback into Pack/core changes, edit Skill files, maintain a refinement decision log, or auto-promote learner comments.

When the user explicitly wants to iterate or improve the Skill from prior learning sessions, use the sibling **`interactive-classroom-refiner`** Skill. Keep the teaching Skill focused on generation, runtime, assessment and learner experience.

## Three learner-quality indicators

For substantial courses, read `references/three-indicator-quality-gate.md`. When `meta.learnerQualityPolicy.mode="three-indicator"`, the course must pass all three independent gates:

1. **Explanation suitability** — prose matches the learner level, bridges prerequisites, establishes a concrete/visual mental model before compression into formal language, defines new terms, includes worked examples, and names at least one boundary or misconception.
2. **Principle-revealing animation** — when animation is used, the changing objects/states must make the target mechanism visible. A decorative motion, node reveal, or moving mind map does not count. The animation must state the principle, observation focus, concrete per-step changes and a debrief/check that asks the learner to explain what the motion demonstrated.
3. **Gap-revealing practice** — practice must do more than count right answers. Guided/independent/transfer items should target distinct likely errors or misconception classes, provide specific feedback, and make it possible to tell *what kind* of misunderstanding remains.

Run `python scripts/audit_three_indicators.py <course.json-or-html>` for the explicit audit in addition to strict HTML validation.

## Course architecture

Use a two-stage generation pipeline:

### Stage A — Course outline / routing

Create internally:

- learning contract and learner level;
- 3–7 observable objectives;
- prerequisite + misconception map;
- **discipline profile** from `references/discipline-router.md`;
- Stage/Scene outline;
- for each interactive scene, choose a `widgetType`;
- objective→assessment evidence map;
- source/evidence boundary.

Do **not** generate final HTML yet.

### Stage B — Specialized scene generation

Generate each scene with the contract appropriate to its kind. For `interactive` scenes, load only the relevant widget reference under `references/widgets/` and follow its quality constraints.

Then compile one final canonical Stage/Scene course model and HTML.

## Canonical scene kinds

Prefer the OpenMAIC-like high-level lesson skeleton:

- `orientation`
- `concept`
- `discussion`
- `interactive`
- `quiz`
- `pbl`
- `reflection`
- `mastery`
- `explain-back` — learner-generated Feynman restatement with non-automatic self-diagnosis

Legacy convenience types remain accepted and normalize into the current typed widget model:

- `whiteboard` → `interactive/diagram`
- `knowledge-graph` → `interactive/diagram`
- `timeline` → `interactive/diagram`
- `simulation` → `interactive/simulation`
- `socratic` → `interactive/game` or `quiz` with a hint ladder, depending on task

## Interactive widget types

OpenMAIC-aligned core types:

- `simulation` — adjustable deterministic process/model;
- `visualization3d` — rotatable 3D-like structures using offline SVG projection;
- `game` — bounded, pedagogical game/challenge;
- `code` — code tracing/debugging; optional native JavaScript sandbox only when explicitly useful;
- `diagram` — flowcharts, mind maps, hierarchies, graphs, timelines, whiteboards;
- `procedural-skill` — ordered procedural/vocational practice with checkpoints.

Cross-disciplinary offline extensions:

- `equation` — native MathML Core formulas, derivations, proofs, worked steps; substantive formulas must not be rendered as monospace/code text;
- `data-lab` — tables, scatter/bar/line plots, interpretation and deterministic calculations;
- `annotation` — text/image-region annotation when source media is embedded;
- `media` — embedded local audio/image/video playback when actual media is available.
- `proof-practice` — deterministic proof ordering / missing-reason practice.
- `quantity-lab` — physical quantities, SI units, dimensions and dimensional-consistency checks.
- `motion-lab` — physics motion studio with synchronized trajectory animation, vector components, time scrubber, graphs and trial comparison.
- `map-lab` — verified offline geographic map with projection/graticule, attribute inspection, spatial filtering and great-circle comparison.
- `data-structure-lab` — stack/queue state operations with visible invariants and operation history.
- `recursion-lab` — call-stack stepper for recursion/base-case/return reasoning.
- `complexity-lab` — adjustable asymptotic-growth comparison; explanatory operation model, not wall-clock benchmark.
- `chemistry` — structured compounds/reactions with atom-conservation checks.

Never add a widget type just to show off interactivity. Use the smallest interaction that improves learning.


## Deep knowledge-first HTML contract

Interactivity is a teaching aid, not the teaching content itself. Every substantial `concept`, `discussion`, `interactive`, and `pbl` scene must contain a learner-visible `knowledge` block. The page must explain the concept even if the learner never touches the widget.

Read `references/deep-explanation.md`. Ordinary “我要学习 X” requests default to the **learn-deep** profile, not a short overview. For formal or theorem-driven material, also read `references/textbook-semantics.md` and represent named definitions/results/proofs/examples/exercises as first-class semantic blocks rather than generic cards. A substantial core concept normally needs enough exposition to stand on its own: prerequisite connection, mental model/intuition, precise definition or mechanism, reasoning chain, worked example, boundaries/misconceptions, forward connection, and a self-check where appropriate.

The canonical `knowledge` object may include `prerequisites`, `mentalModel`, `mechanism`, multi-paragraph `sections`, multiple `workedExamples`, `comparison`, `boundaries`, `connections`, `glossary`, and `checkYourself` in addition to the core fields. Do not fill them mechanically; use the fields needed to complete the learner's reasoning chain.

Worked examples should carry the reasoning chain when the task is nontrivial: `prompt` or statement → direct `figureRef` when a visual is needed → ordered `steps` with formulas and reasons → `result` / `resultFormula`. Do not compress a derivation into one final formula, and do not repeat an experiment prompt only to create more interaction.

Default depth targets are described in `references/deep-explanation.md`. Do not pad with repetition, but do not compress difficult concepts into a few bullet points. A broad topic course should normally focus on 4–8 core concepts and give every objective at least one exposition scene plus one practice/assessment opportunity.

Required learning order for a core scene:

**讲清问题与先修 → 建立直觉/心智模型 → 给出准确表述/机制 → 展开推理链 → worked example / evidence → 边界与误区 → learner interaction → feedback/debrief → takeaway / self-check**.

### Textbook semantic structure

When the discipline naturally uses formal named knowledge, author `knowledge.semanticBlocks` using stable Definition / Lemma / Theorem / Proposition / Corollary / Proof / Example / Exercise / Remark blocks. A central theorem/lemma in a formal course must have a linked proof, proof sketch, justification, or an explicit reason why a proof is omitted. Exercises should depend on already-taught semantic block IDs and may provide progressive hints plus a delayed solution. Do **not** force theorem labels onto empirical laws or interpretive claims. Read `references/textbook-semantics.md`.

Quiz/mastery scenes must not introduce a concept for the first time and must not leak their answers in a pre-test recap.

## Strict mathematics, explanatory motion, and experiments

For any course containing substantive symbolic mathematics, read `references/math-richtext.md` in addition to `references/math-typesetting.md`. Equations and inequalities must not hide in ordinary prose strings. Interleave structured MathML formula atoms with explanation when mathematics occurs inside a reasoning paragraph.

When a diagram explains sequence, construction, causal flow, or state transition, consider `references/animated-explanations.md`. Use deterministic step-based reveal with learner controls (next/play/pause/replay); do not add decorative motion. Essential knowledge must remain available without animation and `prefers-reduced-motion` must work.

For quantitative or experimental learning, read `references/interactive-experiments.md`. Prefer predict → adjust → observe → explain experiments over fixed demonstrations whenever a deterministic local model exists. `simulation`, `data-lab`, `quantity-lab`, and chemistry balancing scenes should expose meaningful learner control under `meta.experimentPolicy="adjustable-when-applicable"`.

Give each structured experiment a unique `experimentKey` and `experimentRole`, plus controlled/changed variables and an evidence question. Set `meta.experimentDedupPolicy="stable-key"` when using that contract; exact duplicate prompts and repeated keys are rejected by strict validation.

## Grounded textbook infrastructure

For substantial courses, especially when the user supplies files or asks for rigorous study, use `course.sources` plus local `citations` instead of a detached bibliography. Read `references/source-citation.md`. A source has a stable ID; citations may add a locator/note. The runtime renders numbered citation chips, a per-scene source trail and a full-course bibliography dialog. Strictly offline HTML may store bibliographic text, but must not fetch remote content.

Set `meta.autoNumbering=true` by default. The renderer assigns stable stage-based numbers to Definition/Lemma/Theorem/Proposition/Corollary/Example/Exercise blocks and to formulas with stable formula IDs. Cross references may target either semantic-block IDs or formula IDs. Explicit author numbers remain supported for imported material, but newly generated courses should normally let the renderer number automatically.

Use `meta.sourcePolicy="grounded"` when every substantial core scene should visibly cite at least one declared source; the validator rejects missing/unknown citations. For a general conceptual course without external sources, `recommended` is acceptable, but do not invent bibliography entries.

## Proof Practice and subject-specific learning contracts

Read the relevant references when the discipline requires them:

- `references/proof-practice.md` — proof ordering and reason matching;
- `references/quantity-units.md` — physics/engineering quantities, SI units and dimensions;
- `references/chemistry-reactions.md` — structured formula/reaction data and atom conservation;
- `references/long-course-navigation.md` — search, session bookmarks and bibliography navigation;
- `references/math-richtext.md` — prevent equations from leaking into ordinary prose;
- `references/animated-explanations.md` — deterministic staged explanatory animation;
- `references/interactive-experiments.md` — learner-adjustable offline experiments.
- `references/widgets/motion-lab.md` — synchronized motion representations, fixed comparison scales, time control and trial logging for mechanics.
- `references/process-animation.md` — the shared timeline, semantic-step, autoplay and reduced-motion contract used by both renderers.

Proof practice must depend on a proof/derivation already taught. Physics equations should declare units/dimensions when dimensional reasoning is pedagogically relevant. Chemistry equations used for balancing practice should use structured atom counts so the runtime can deterministically verify conservation; never “balance” by changing compound subscripts.

The long-course shell includes session-only search and bookmarks. Do not imply bookmarks persist after the HTML is closed unless a persistence mechanism is explicitly added.

## Discipline Router

Read `references/discipline-router.md` before planning a substantial course. Infer one primary profile and optional secondary profiles:

- formal/quantitative — math, logic, theoretical CS;
- physical/experimental — physics, chemistry, engineering;
- life/clinical — biology, medicine, health sciences;
- computational/data — programming, algorithms, statistics, data science;
- social/decision — social science, economics, management, policy, law;
- historical/interpretive — history, philosophy, literature, cultural studies;
- language/communication — language learning, rhetoric, writing;
- visual/spatial/creative — geography, art, design, architecture;
- procedural/vocational — lab technique, engineering procedures, vocational skills.

The router changes scene choices, evidence standards and assessment forms; it must not change factual content without evidence.

## Classroom roles

For substantial courses, use explicit subagents when available or independent review passes:

- **Teacher** — sequence and explanation;
- **Curious Student** — prerequisites and beginner questions;
- **Skeptic** — counterexamples, edge cases, weak inference;
- **Evidence Reviewer** — source fidelity and uncertainty;
- **Examiner** — objective-aligned assessment/remediation;
- **Visual Director** — scene/widget choice, visual coherence, cognitive load;
- **Discipline Specialist** — checks notation, conventions, domain validity;
- **Moderator** — optional for multi-perspective discussion.

These roles are generation-time roles. In the HTML they appear only as symbolic, pre-generated classroom identities.

## Teacher Action Protocol

The runtime supports an offline analogue of OpenMAIC's agent→widget guidance. Scenes may contain an `actions` timeline. The browser executes only declared local actions through the local Action Bus.

Supported core actions:

- `HIGHLIGHT_ELEMENT`
- `CLEAR_HIGHLIGHT`
- `SELECT_ELEMENT`
- `SET_WIDGET_STATE`
- `REVEAL_STEP`
- `SHOW_HINT`
- `RESET_WIDGET`
- `FOCUS_REGION`

Read `references/action-protocol.md`. Every interactive widget must implement applicable actions consistently. Teacher guidance must never silently no-op.

## Modes

`ic-learn` — internal/default zero-config route for ordinary natural-language learning requests; users do not need to type it.


These are prompt aliases, not shell commands:

- `ic-build` — complete classroom from topic/materials;
- `ic-teach` — guided Socratic/Feynman lesson;
- `ic-dialogue` — multi-role discussion;
- `ic-widget` — build one specialized interactive widget;
- `ic-simulate` — simulation;
- `ic-3d` — offline 3D-like visualization;
- `ic-code` — code-trace/debugging lesson;
- `ic-game` — bounded learning game;
- `ic-diagram` — graph/flow/timeline/whiteboard;
- `ic-data` — data lab;
- `ic-equation` — derivation/proof/formula lesson;
- `ic-procedure` — procedural/vocational practice;
- `ic-pbl` — project/problem-based learning;
- `ic-quiz` — diagnostic/mastery assessment;
- `ic-revise` — patch existing course while preserving stable IDs;
- `ic-audit` — pedagogy, domain validity, accessibility, offline/runtime audit.

## Workflow

### 1. Establish learning contract automatically

For topic-only or ordinary learning requests, read `references/auto-orchestration.md` and `references/deep-explanation.md`.

Infer topic, learner level, outcomes, evidence boundary, language, interaction depth, available source/media, and output path. A topic-only request is sufficient. Do not ask the user to choose discipline labels, widgets, roles, scene types, or validator options. Do not ask questions that are not necessary to make progress.

When user files are provided, treat them as primary evidence. Do not fabricate claims, citations, numeric constants, experiment results, legal rules, clinical facts, or model parameters.

### 2. Run discipline routing

Use `references/discipline-router.md` to select the primary discipline profile. Add a `Discipline Specialist` review pass for substantial courses.

### 3. Generate the outline only

Before HTML, create internally:

- stages;
- scene IDs/titles/types;
- objective IDs;
- `widgetType` for each interactive scene;
- assessment evidence;
- agent/action opportunities;
- source/media requirements.

Do not force every widget into the course.

### 4. Generate deep, knowledge-first scenes with specialized contracts

Read `references/scene-contract.md`, `references/deep-explanation.md`, `references/textbook-semantics.md` when applicable, and the one relevant widget reference per interactive scene. Before widget/decision controls, author a substantial explanation. For ordinary learning requests, do not treat `summary + 3 bullets + one tiny example` as sufficient coverage of a difficult concept.

Key rules:

- `simulation`: visible assumptions, units, prediction, parameter changes, interpretation;
- `visualization3d`: meaningful spatial structure, labels, rotate/reset, text fallback;
- `game`: explicit learning target, finite rounds, transparent scoring, debrief;
- `code`: language shown, expected reasoning target, code trace/tests, no fake runtime;
- `diagram`: relation semantics, selection/details, keyboard alternative to drag; when a process unfolds over time, add staged next/play/pause/replay animation rather than decorative motion;
- `motion-lab`: for kinematics, synchronize the moving object, trajectory, velocity components, time scrubber, x–t/y–t graphs and derived quantities; use fixed comparison scales and let learners record multiple trials;
- `procedural-skill`: ordered steps, hazards/constraints, checkpoints, remediation;
- `equation`: notation defined, derivation steps justified, Modern visibly reveals one step at a time with reason/reset controls, and the learner predicts the next step when useful;
- `data-lab`: provenance/units, visible data, deterministic calculations, interpretation; when parameters are learnable, let the learner adjust them and update model outputs/metrics live;
- `annotation`: selectable regions/spans and evidence-grounded labels;
- `media`: only embed actual available local media; never invent audio/video.

### 5. Add classroom roles + local actions

Use a Stage-level roster. If a teacher/peer is supposed to guide an interactive widget, encode the guidance as declared scene actions. Do not write narration that refers to UI changes that never happen.

### 6. Assessment

Read `references/assessment.md`.

Offline deterministic kinds include:

- single choice;
- multiple choice;
- numeric tolerance;
- exact/normalized short answer;
- ordering;
- matching;
- classification;
- code-output/trace;
- equation-step selection;
- self-rubric for free-form explain-back.

Never call keyword matching “AI grading.”

### 7. PBL / procedural learning

For PBL use role + mission + resources + milestones/microtasks + decisions + deterministic consequences + debrief. For procedural skill learning, distinguish **practice/checklist simulation** from real-world certification or safety-critical competency.

### 8. Compile with the selected frontend runtime

First read `references/frontend-runtime.md`, then choose the renderer. For `portable`, start from `assets/classroom-shell.html`. For `modern-react`, start from `assets/modern-runtime/`, generate only the components/widgets the course needs, and run its generation-time build so React/Motion and compiled Tailwind CSS are inlined into the final HTML.

Default learner output remains:

`interactive-classroom-<slug>.html`

Requirements for **both** profiles:

- one offline HTML delivery artifact by default; source workspace/build dependencies are not part of learner delivery;
- calm textbook/documentation visual system from `references/visual-system.md` + `references/visual-inspiration.md`;
- wide-screen layout: course outline (left) + reading page (center) + current-page knowledge outline (right);
- learner-visible knowledge explanation before/alongside core interaction;
- substantive equations/inequalities rendered through structured native MathML, including when embedded between explanatory paragraphs;
- explanatory diagrams may use bounded staged animation with learner-controlled playback;
- practice widgets expose learner-adjustable variables when a deterministic experiment is applicable;
- geometry/spatial learning uses explanatory figures where verbal/symbolic exposition alone is likely to leave an incorrect mental model; figures must state what to notice and what cannot be inferred from the drawing;
- embedded or bundled HTML/CSS/JS/course data;
- no external model/API/server by default;
- **no learner-side build step**; the `modern-react` profile may build during Codex generation;
- direct `file://` open for the delivered artifact;
- responsive ~320 px and up;
- keyboard-usable primary interactions;
- reduced-motion support;
- visible offline/privacy note;
- no learner-facing `undefined`, `NaN`, `Infinity`;
- in-scene interactions preserve the current scroll position;
- scene navigation scrolls to the next scene heading rather than the document top;
- current-page TOC anchors must not re-render the scene.

Embedded `data:` media is allowed. Remote media is not allowed in strict offline mode.

### 9. Stable Stage/Scene DSL and patchable revision

Use `references/course-schema.md`.

Preserve stable IDs. For `ic-revise`, prefer atomic scene-level data changes over rewriting unrelated scenes. Re-run validation after every meaningful revision.

### 10. Validate

Run:

```bash
python scripts/validate_skill.py .
python scripts/validate_frontend_runtime.py .
python scripts/test_runtime_routing.py
python scripts/test_modern_runtime.py
python scripts/test_cross_runtime_animation.py
python scripts/check_python_syntax.py .
python scripts/audit_visual_style.py assets/classroom-shell.html
python scripts/audit_modern_visual_style.py assets/modern-runtime/src/styles.css
python scripts/run_regression.py
python scripts/test_negative_gates.py
python scripts/validate_html.py path/to/classroom.html --strict
```

For release validation, run the bundled version-neutral regression suite and keep every strict HTML check at 0 warnings. The suite covers physics, biology, chemistry, machine learning, artificial intelligence, geography, computer science, statistics, language, humanities, and social science, while the canonical Mathematics example additionally exercises source coverage, mastery-loop practice, MathML, process animation, random trials, explain-back, and objective-level mastery. `scripts/test_modern_runtime.py` verifies that the bundled corpus is also covered by the Modern teaching contract and built-in widget baseline. These fixtures intentionally test different epistemic and interaction patterns rather than one favored subject.


### Mathematical typesetting invariant

For mathematics, physics, statistics, cryptography, economics, chemistry, engineering, or any scene containing substantive symbolic notation:

- author formulas as structured `formula` objects with native MathML Core plus a `tex`/spoken fallback;
- never leave a substantive equality, inequality, congruence, summation, limit, or model equation embedded only in a normal prose string; use rich narrative formula atoms;
- use `display="block"` MathML for derivations and major equations; use inline MathML only for short symbols/relations;
- never use code blocks or monospace text as the primary mathematical renderer;
- define notation before use, preserve intermediate steps, label assumptions/domain restrictions, and give a textual explanation of what each formula means;
- mathematical proofs should use semantic `proof` blocks with one non-trivial inference per step and explicit reasons; theorem/lemma claims should link to their justification;
- do not depend on KaTeX/MathJax/CDN/font downloads in strict offline mode.

Read `references/math-typesetting.md` when formulas are present.

## Physics multi-representation invariant

For motion topics, do not reduce understanding to a single trajectory plot. When the target concept depends on decomposing motion or linking equations to observations, prefer a synchronized **multi-representation** scene: physical animation + vector components + time graphs + numerical readout + learner-controlled parameters + recorded trials. Keep plot scales fixed across parameter changes when comparison is the learning goal. Distinguish measured/controlled variables from derived quantities, and teach a control-variable experiment rather than inviting random slider play.

## Pedagogical invariants

1. Elicit before reveal when appropriate.
2. One dominant learning purpose per scene.
3. Misconceptions get specific remediation.
4. Evidence, inference, simulation and illustration are labeled separately.
5. Visuals/interactions serve reasoning, not decoration.
6. Mastery uses observable evidence, not completion clicks.
7. Free-form prose is self-assessed offline unless a real model connection is explicitly added.
8. Domain conventions and safety constraints override generic classroom aesthetics.
9. Deep explanation comes before decorative density: the HTML must remain useful even if every widget is ignored.
10. Re-rendering an interaction must not unexpectedly reset the reader to the page top.
11. Formal knowledge has explicit epistemic structure: definitions, claims, proofs, examples and exercises are distinguishable and cross-referenceable when the discipline warrants it.
12. Sources are part of the learning model, not decoration: important claims should visibly connect to declared evidence or textbook sources when sourcePolicy is grounded.
13. Subject-specific validity outranks generic UI: physics quantities preserve units/dimensions, chemistry preserves compound identity and atom conservation, and proof practice preserves logical dependencies.
14. Search/bookmarks improve long-course navigation but do not count as learning or mastery evidence.
15. Motion must explain sequence/change and remain controllable; animation never substitutes for exposition.
16. When a concept has meaningful parameters, practice should prefer learner-controlled experiments with visible model response over fixed screenshots or fixed numbers.

## Important limitations

- No live free-form LLM chat inside strict offline HTML.
- `code` is guaranteed for deterministic code tracing; arbitrary multi-language execution requires an embedded runtime and is not assumed.
- `visualization3d` may use the existing offline SVG projection or a locally bundled WebGL/Three.js-style implementation when complexity warrants it; remote CDN runtime dependencies remain disallowed by default.
- Audio/speech requires embedded source media or browser-native capabilities; no cloud TTS/ASR is assumed.
- Medical, legal, laboratory and safety-critical teaching must clearly distinguish educational practice from professional certification/real-world action.


## Validated-native pack notes

For Geography, read `discipline-packs/geography/PACK.md` and `references/widgets/map-lab.md`. Verified geography must remain embedded/offline, disclose projection/scale and provenance, and use spatial reasoning tasks rather than pin lookup.

For Computer Science, read `discipline-packs/computer-science/PACK.md` and the `data-structure-lab`, `recursion-lab`, and `complexity-lab` widget references. Separate abstract data structure semantics, runtime/call-stack state, and asymptotic models; never call a deterministic trace “real execution.”
## Native Language / Humanities / Social Science notes

- **Language** is validated-native for deterministic reading/grammar/writing structure practice through `cloze-lab`, `sentence-builder-lab`, and `grammar-tree-lab`. Listening is supported only when audio is actually embedded. Pronunciation scoring remains unavailable without a real speech engine.
- **Humanities** is validated-native for source comparison and argument structure. Preserve text status (`quote`, `paraphrase`, `summary`, `translation`), source provenance, historical context and perspective. Do not collapse interpretation into fact.
- **Social Science** is validated-native for causal-assumption reasoning and evidence-strength comparison. A DAG encodes assumptions, not truth; observational association must not be described as causal identification without an appropriate design/assumption contract.

### Learning feedback is not hidden telemetry

The runtime feedback dialog records only explicit learner entries. Export occurs only after a learner action and produces a local session-feedback JSON file. The HTML must not call network endpoints, persist silent analytics, infer protected/sensitive attributes, or mutate Skill files. Any later Skill iteration is a separate explicit workflow handled by `interactive-classroom-refiner`.


## Reader-first visual quality

For substantial learner-facing courses, set `meta.visualQualityPolicy.mode="reader-first-accessible"` together with the three-indicator quality gate. Use `minTextContrast>=4.5`, `minNonTextContrast>=3.0`, `animationLabelMinPx>=14`, `avoidColorOnlyEncoding=true`, and `mobileAnimationStrategy="scroll-inside"`.

Do not shrink wide process animations until labels become illegible on phones. Keep the animation canvas internally scrollable while preventing page-level horizontal overflow. Process actors must use explicit semantic `background + stroke + text` color triples in both light and dark mode. Never assume `var(--text)` is readable on every actor fill. Run `python scripts/audit_visual_style.py assets/classroom-shell.html` before release.

Visual polish remains subordinate to learning: prefer whitespace, editorial hierarchy, readable line measure, and quiet navigation over gradients, heavy shadows, nested cards, or decorative motion. Color is never the sole carrier of meaning.

## Learner-first surface and process animation

Read `references/learner-facing-contract.md` and `references/animated-explanations.md`.

Keep `sourceCoverage`, `contentInventory`, internal schema metadata, Pack routing, validator status and refinement mechanics internal in normal learner HTML. Show bibliography/citations when useful, but do not turn the lesson into an authoring report. Use `meta.learnerSurfacePolicy.hideEngineering=true` for learner-facing courses.

A staged node/edge reveal is not evidence of animation. Use `process-animation` when the learner needs to see a principle unfold through actual object/state change. Under `meta.animationPolicy.mode="process-first"`, strict validation rejects staged diagram animation as the required process animation. Every process step should state the observation focus and the concrete change that occurs. Prefer concrete actors such as a die, coin, moving body, molecule, search node, or measured quantity over generic labeled boxes when the subject permits. Declare `layoutPolicy.preventOverlap=true`, a safe margin, and a minimum actor gap; use explicit containment zones when objects intentionally enter a region. Background tracks/zones render before moving actors so explanatory regions never paint over the process. Long prose belongs below the animation, not on top of moving paths. Use `random-trial-lab` for adjustable repeated random experiments.


## Content-fit animation planning

Before generating animation, classify the target as mechanism-process, dynamic-quantity, structure-build, reasoning-evolution, simulation-experiment, or static-relation. Read `references/animation-content-fit.md` and `references/discipline-animation-profiles.md`. Do not animate a static relation merely to add motion.

Every content-fit `process-animation` must declare `animationSemantics` (discipline profile, conceptual entities, state variables, semantic step logic, motion rationale, and `mustNotMislead`). Give actors semantic roles, give each step `semanticAction` and `whyItMatters`, slow down at least one key state change, and prefer discipline-native primitives or a native lab. A valid animation must pass both principle-revealing and content-fit audits: the right objects move in the right way for the right reason.

Run `python scripts/audit_animation_content_fit.py <course>` before release.

### Shared process-animation runtime contract

`process-animation` defaults to playing the current timeline once when its scene is mounted. It must never advance the course scene by itself. `autoplay:false` is an explicit opt-out, and `loop:true` is an explicit request to repeat the timeline. The learner can pause, replay, select a discrete step, and use the keyboard-accessible controls. Portable uses requestAnimationFrame sampling for actor state transitions; Modern uses the same semantic state contract with component transitions.

The shared fields are `autoplay`, `loop`, `timeline`, `actors` (or the legacy `entities` alias), and `steps`. Each step must state `semanticAction`, `focus`, `changeSummary`, and `whyItMatters`, and its `states` must describe an observable change in a named actor. `animationSemantics` describes the discipline profile, state variables, motion rationale and permitted semantic relations; it does not change the timeline controls. Chemistry, biology, language, statistics, computer science and social-science scenes should select their own concrete primitive adapter rather than a generic placeholder.

When the learner or operating system requests reduced motion, automatic progression and interpolation are disabled while the discrete state, caption, pause/replay controls and direct step selection remain available. If a requested native widget is not implemented, the generation stage must explicitly fall back to portable or fail with a capability error; a `GenericLab` placeholder is not a deliverable.

### Semantic contact and crafted learner surface

Use `meta.animationContentPolicy.mode: content-fit` for courses that rely on mechanism animation. When actors intentionally touch, overlap, enter, contain, pass through, attach, or point, declare `animationSemantics.semanticRelations`; otherwise normal collision rules still apply. Use optional `whenSteps` with semantic-action names so contact permission only exists during the exact mechanism steps where it is conceptually valid. See `references/animation-content-fit.md` and `references/frontend-craft.md`.

The learner surface may borrow restrained craft principles from modern interfaces, but the course remains a reader-first offline textbook. Decorative motion must never count as pedagogical animation, active-state styling must not cause layout shifts, and process timelines must be interruptible and directly addressable.


## Modern frontend implementation

React, Tailwind and Motion are permitted when they improve component/state quality. They are not a license for decorative app chrome or runtime network dependencies. Read `references/frontend-runtime.md`. Modern courses must preserve the same knowledge-first, source, math, assessment, animation-content-fit, accessibility and scroll-state contracts as the portable renderer. The built-in registry must expose real implementations for every used teaching widget, including `process-animation`, `motion-lab`, `simulation` and `equation`; capability declarations and the registry are checked together before build.
