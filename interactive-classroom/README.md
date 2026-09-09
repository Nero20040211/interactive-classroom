# interactive-classroom v1.0.0

**Knowledge-first, cross-disciplinary interactive learning Skill for Codex.**

A natural request such as `我要学习密码学`, `教我高中物理平抛运动`, or `带我系统学习二分查找` is enough. The Skill infers learner level and discipline, builds a Stage/Scene course plan, teaches knowledge before or alongside interaction, and produces an offline classroom.

## Release identity

- Current public release: **v1.0.0**.
- This release number is documentation only. It does **not** participate in runtime routing, course generation, validation gates, renderer choice, regression selection, or learner-state compatibility.
- Executable files use stable semantic contracts and capability-driven checks instead of release-number branches.

## Runtime profiles

- **portable** — zero-build single-file HTML using `assets/classroom-shell.html`.
- **modern-react** — React + compiled Tailwind CSS + Motion, bundled locally at generation time into the learner HTML.

The runtime is selected by learner intent plus implementation complexity, not prestige. Simple/medium ordinary requests stay portable. A request such as **“我需要一个详细讲解……的课程”**、**“我需要一个详细的讲解……”**, **“请精细/深入/详尽讲解……”**, or **“I want a detailed/in-depth interactive course on …”** is a direct natural-language trigger for the modern profile when the toolchain is available. State-dense, synchronized, animation-rich, custom-visualization, or explicitly React-oriented courses also use the modern profile. Explicit `portable` / `zero-build` / `不要 React` constraints take precedence.

Pinned generation-time scaffold dependencies are React/React DOM **19.2.8**, Tailwind CSS **4.3.3**, Motion **13.1.1**, and esbuild **0.28.2**. These are third-party toolchain pins, not Interactive Classroom release identifiers.

The Modern Runtime has fixed renderers for the core teaching loop (orientation/concept, quiz, explain-back, mastery, discussion/PBL/reflection/checkpoint, textbook semantic blocks, pedagogical figures, citations and feedback) plus a built-in cross-disciplinary widget baseline. Course-specific React widgets may still extend the explicit generated registry.

Process animation is a shared semantic contract across both profiles: it plays the current timeline once by default, exposes pause/replay/direct-step controls, and never changes the course scene automatically. `autoplay:false` and `loop:true` are explicit configuration choices. Every step names its focus, observable change, semantic action and instructional consequence. Reduced motion keeps the inspectable discrete states and controls while disabling automatic progression and interpolation. Native discipline primitives are required; `GenericLab` is not a valid delivery widget.

The Modern learner surface uses the B-style learning workbench: a sticky course header, scene rail, reader-first central column, optional current-page outline rail, and offline footer. The layout collapses at narrow widths while keeping internal animation canvases scrollable and the reading position stable.

### Quick Modern Runtime invocation

You do not need to name the runtime. In Codex, requests such as the following are enough:

- `我需要一个详细讲解高中物理平抛运动的课程`
- `请精细讲解二分查找，并做成交互课程`
- `把递归讲得更详细一点`
- `I want an in-depth interactive course on cell respiration`

The Skill treats these depth signals as a Modern Runtime preference. Say `portable`, `zero-build`, `不要 React`, or `只要轻量单文件` when you explicitly want the portable path.

## Core guarantees

- **Knowledge first:** prerequisites, mental model, precise definition/mechanism, reasoning, worked examples/evidence, boundaries/misconceptions, then practice.
- **Direct teaching figures:** spatial/mechanical/structural/process worked examples can bind an implemented offline figure with `figureRef`; direct figures are preferred to text-only examples or mind-map-like decoration.
- **Textbook semantics:** Definition / Lemma / Theorem / Proposition / Corollary / Proof / Example / Exercise / Remark where appropriate.
- **Strict mathematics:** substantive equations/inequalities use structured native MathML plus TeX/spoken fallback instead of disguised prose/code formulas.
- **Principle-revealing animation:** animation must expose a mechanism or state change; decorative UI motion never counts as teaching animation.
- **Learner-adjustable experiments:** predict → adjust → observe → explain when a deterministic parameterized model is appropriate.
- **Experiment deduplication:** structured experiment prompts use unique `experimentKey` / `experimentRole` pairs so a course does not repeat the same comparison under different wording.
- **Discipline Packs:** mathematics, physics, chemistry, biology, statistics, ML/AI, computer science, geography, language, humanities, social science, and procedural/vocational learning.
- **Assessment honesty:** deterministic checks are not called AI grading; open prose is self-diagnosis unless a real model is explicitly connected.
- **Offline learner runtime:** no required server, external LLM key, CDN, fetch, WebSocket, analytics, or hidden live model by default.

## Modern frontend policy

`references/frontend-runtime.md` defines runtime routing and implementation rules; `scripts/select_runtime.py` provides a deterministic natural-language fast-path check. Modern courses keep the Stage/Scene course model framework-neutral, use local state boundaries, stable IDs, learner-safe error boundaries, sanitized MathML, reduced-motion handling, local learning-feedback export, and the same reader/source/assessment contracts as the portable runtime. Every used widget must exist in both the modern widget manifest and React registry before build. Modern knowledge rendering preserves worked-example figures, intermediate formulas, step reasons, comparison tables, and takeaways instead of reducing them to plain text.

## Regression philosophy

The bundled regression suite is version-neutral and renders fixtures with the **current** portable shell every run. It covers:

- physics;
- biology;
- chemistry;
- machine learning;
- artificial intelligence;
- geography;
- computer science.

The canonical Mathematics example additionally exercises grounded sources, source coverage, MathML, process animation, random trials, explain-back, practice progression, and an independent mastery gate. Negative tests deliberately inject bad version metadata, raw math leakage, unresolved citations, invalid geographic coordinates, broken stack invariants, missing animation semantics, unresolved worked-example figures, repeated experiment keys, and overused mind-map-like diagrams to verify that strict validation rejects them.

## Install

Copy `interactive-classroom` to:

- Windows: `%USERPROFILE%\.codex\skills\interactive-classroom`
- macOS/Linux: `~/.codex/skills/interactive-classroom`

The formal archive now includes `interactive-classroom-refiner` as a sibling Skill. Copy both sibling directories into the Codex Skills directory if you want the complete teaching → explicit feedback → reviewed refinement workflow. The teaching Skill never mutates itself automatically.

## Static release validation

```bash
python scripts/validate_skill.py .
python scripts/validate_frontend_runtime.py .
python scripts/test_runtime_routing.py
python scripts/test_cross_runtime_animation.py
python scripts/audit_visual_style.py assets/classroom-shell.html
python scripts/audit_modern_visual_style.py assets/modern-runtime/src/styles.css
python scripts/run_regression.py
python scripts/test_negative_gates.py
python -m compileall -q scripts
```

Render and validate a portable course:

```bash
python scripts/render_course.py examples/example-course.json /tmp/classroom.html
python scripts/validate_html.py /tmp/classroom.html --strict
python scripts/validate_mastery_gate.py /tmp/classroom.html
```

`validate_mastery_gate.py` returns PASS / not applicable when a course does not declare `practicePolicy.mode="mastery-loop"`.

For a modern course, also run the actual npm build and browser smoke in the target Codex environment. Those environment-dependent checks are intentionally not claimed by the portable/static release suite.

## Windows Modern build and browser smoke

After generation has placed a real course in `assets/modern-runtime/src/course.generated.json` (the checked-in `replace-me` scaffold is intentionally rejected), run the clean generation-time install and build from `assets/modern-runtime/`:

```powershell
npm ci --ignore-scripts
npm run build
python ..\..\scripts\validate_html.py dist\interactive-classroom.html --strict
```

The build inlines Tailwind CSS once, bundles the pinned React/Motion runtime, and writes only the learner-facing `dist/interactive-classroom.html`; do not ship `node_modules`, `.build`, `dist` caches or source maps. To inspect both profiles locally, serve the package root with `python -m http.server 8765`, then open the generated Modern HTML and a portable HTML under `test-output/` in a browser. Check scene autoplay → pause → replay, semantic state changes, native widget controls, MathML/fallback, keyboard focus, reduced motion and the 390 px responsive layout. Stop the local server after the smoke check.

## Key references

- `references/frontend-runtime.md`
- `references/process-animation.md`
- `references/deep-explanation.md`
- `references/textbook-semantics.md`
- `references/math-typesetting.md`
- `references/interactive-experiments.md`
- `references/animation-content-fit.md`
- `references/pedagogical-figures.md`
- `references/widgets/equation.md`
- `references/practice-progression.md`
- `references/mastery-practice-loop.md`
- `references/discipline-packs.md`
- `references/three-indicator-quality-gate.md`
