# Course Schema 

This is an internal convention, not a claim of `@openmaic/dsl` compatibility.

```js
const course = {
 meta: {
 id: "course-id",
 title: "...",
 subtitle: "...",
 language: "zh-CN",
 level: "undergraduate",
 offline: true,
 discipline: {
 primary: "formal-quantitative",
 secondary: []
 }
 },
 objectives: [{ id: "O1", text: "...", evidence: "..." }],
 misconceptions: [{ id: "M1", text: "...", repair: "..." }],
 stages: [
 {
 id: "ST1",
 title: "...",
 roster: ["teacher", "curious", "skeptic", "specialist"],
 sceneIds: ["S1", "S2"]
 }
 ],
 roles: [
 { id: "teacher", name: "老师", function: "...", avatar: "师", tone: "teacher" }
 ],
 scenes: [
 {
 id: "S2",
 stageId: "ST1",
 type: "interactive",
 title: "...",
 objectiveIds: ["O1"],
 knowledge: {
 title: "本节知识",
 summary: "...",
 intuition: "...",
 semanticBlocks: [
 { id: "def-1", kind: "definition", number: "1.1", title: "...", body: "..." },
 { id: "thm-1", kind: "theorem", number: "1.1", statement: "...", references: ["def-1"] },
 { id: "proof-1", kind: "proof", of: "thm-1", steps: [{ text: "...", reason: "..." }] },
 { id: "ex-1", kind: "example", number: "1.1", prompt: "...", steps: ["..."] },
 { id: "exr-1", kind: "exercise", number: "1.1", prompt: "...", dependsOn: ["thm-1"], hints: ["..."], solution: "..." }
 ],
 pitfalls: ["..."],
 takeaway: "..."
 },
 content: {
 widgetType: "equation",
 widgetConfig: {}
 },
 actions: []
 }
 ]
};
```

## Stable IDs

Preserve course/stage/scene/objective/misconception/role/widget-element IDs during content-only revision.

## High-level scene types

- orientation
- concept
- discussion
- interactive
- quiz
- pbl
- reflection
- mastery

## Interactive content

```js
content: {
 widgetType: "simulation",
 widgetConfig: { ... },
 summary: "text fallback"
}
```

## Runtime state

Learner state is separate from the course model. Do not mutate authored content during normal interaction.


## Knowledge block

`knowledge` is required for substantial `concept`, `discussion`, `interactive`, and `pbl` scenes. It is rendered before the interaction zone. Quiz/mastery may include a non-answer-leaking recap, but assessed knowledge must have been taught in an earlier scene.

## deep-explanation and math extension

The `knowledge` object remains backward-compatible, but allows richer fields for self-sufficient teaching: `prerequisites`, `mentalModel`, `mechanism`, `sections`, `workedExamples`, `comparison`, `boundaries`, `connections`, `glossary`, and `checkYourself`. See `deep-explanation.md`.

For ordinary learning requests, set `meta.depthProfile` to `learn-deep` unless the user explicitly asks for an overview. Stable scene IDs remain unchanged when enriching explanation depth.


## Textbook semantic blocks

`knowledge.semanticBlocks` is optional but recommended when the discipline has named definitions/results/proofs/exercises. IDs are global within a course. `proof.of`, `references`, and `dependsOn` refer to those IDs. See `textbook-semantics.md`.

## Formula object

```js
formula: {
 tex: "...",
 spoken: "...",
 label: "式 1",
 mathml: "<math display=\"block\">...</math>"
}
```

Use this in knowledge sections, semantic blocks, worked-example/proof steps, and equation widget steps. Plain string formulas are legacy fallback only.


## Grounded sources and citations

```js
meta: { autoNumbering: true, sourcePolicy: "grounded" },
sources: [
 { id:"src-1", title:"...", author:"...", year:"...", edition:"...", note:"..." }
]

// citations may appear on knowledge, semantic blocks, formula objects, or other authored claim containers
citations: [
 { sourceId:"src-1", locator:"Chapter 3 / p. 42", note:"supports this definition" }
]
```

Stable semantic block IDs and formula IDs are cross-reference targets. With `autoNumbering:true`, explicit `number`/`label` is optional; the renderer assigns stage-based numbers.

## additions

### Course experiment policy

```json
"meta": {"experimentPolicy":"adjustable-when-applicable"}
```

### Rich mathematical narrative

Narrative fields may be arrays of prose/formula atoms. See `math-richtext.md`.

### Animated diagram

`interactive/diagram.widgetConfig.animation` controls deterministic staged reveal. Nodes/edges may include integer `step` fields. See `animated-explanations.md`.

### Adjustable experiments

`data-lab`, `quantity-lab`, `simulation`, and `chemistry` may expose deterministic local controls. See `interactive-experiments.md`.

## native interpretive/language/social widgets

Additional `interactive` scene `widgetType` values:

- `cloze-lab`
- `sentence-builder-lab`
- `grammar-tree-lab`
- `source-comparison-lab`
- `argument-map-lab`
- `causal-dag-lab`
- `evidence-matrix-lab`

For substantial courses, `meta.disciplinePack` remains required. Language/Humanities/Social Science native scenes should follow their Pack contracts rather than generic widget payloads.

The session-feedback export is **not part of the course JSON**. It is generated at runtime only from learner-explicit feedback and follows `interactive-classroom-session-feedback`. Skill refinement is handled separately by `interactive-classroom-refiner`.

## additive fields

### `meta.figurePolicy`

```json
{
 "figurePolicy": {
 "mode": "geometry-native",
 "minFiguresPerCore": 2,
 "requireKindDiversity": true,
 "requireSourceBinding": true
 }
}
```

### `knowledge.pedagogicalFigures`

See `pedagogical-figures.md`. These are explanation blocks, not runtime widgets.

### Worked-example figures and direct-first visual policy

A worked example may bind an explanation-first figure without duplicating the figure in a gallery:

```json
{
  "id": "ex-trajectory",
  "title": "先读分量",
  "visualNeed": "mechanical",
  "figureRef": "fig-trajectory-components",
  "steps": [{"text": "先分别读两个方向的分量。", "reason": "共同时间让两个坐标描述同一个物体。"}],
  "result": "再用模型解释轨迹。"
}
```

`figureRef` must resolve to a figure in the same `knowledge` block. Modern and portable renderers place the referenced pedagogical figure inside the worked example. `template:"motion-components"` is an offline SVG teaching figure for mechanics; it is not a remote image. Other direct templates remain available through the Pack registry.

For a course that should prefer direct instructional figures over mind-map-like diagrams, declare:

```json
"figurePolicy": {
  "mode": "direct-first",
  "preferDirectFigures": true,
  "requireWorkedExampleFigure": true,
  "maxMindMapLikeDiagrams": 1
}
```

Under `direct-first`, examples with `visualNeed` of `spatial`, `mechanical`, `structural`, `process`, `dynamic`, or `geometry` need a `figureRef`. Mind-map-like `diagram` scenes (`mind-map`, `knowledge-graph`, `hierarchy`) must declare a genuine `visualPurpose` and `mindMapJustification`; additional diagrams beyond the cap require an explicit justification. A direct figure is preferred when the target is an object, comparison, mechanism, construction, or misconception rather than a hierarchy/network.

### `contentInventory[].figureRefs`

Stable references used by the geometry quality gate.

### Worked-example diversity

When `practicePolicy.requireExampleContrast=true`, referenced worked examples should declare `variantType` (`standard`, `contrast`, `boundary`, `misconception`, or `reverse`).

### Experiment identity and deduplication

Experiment prompts may be structured objects so the generator can preserve the learning role and control variables:

```json
{
  "experimentKey": "speed-vs-range",
  "experimentRole": "control-variable",
  "prompt": "保持高度与重力不变，只改变初速度。",
  "controlledVariables": ["h", "g"],
  "changedVariables": ["v0"],
  "evidenceQuestion": "哪一个派生量改变，哪一个保持不变？"
}
```

Keys are stable within a course and must not repeat. Exact duplicate prompts are also rejected. Set `meta.experimentDedupPolicy:"stable-key"` when every structured experiment entry must declare both `experimentKey` and `experimentRole`; this prevents repeated copies of the same experiment from accumulating under different wording while preserving legacy string prompts in older courses.
