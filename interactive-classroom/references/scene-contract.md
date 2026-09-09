# Scene Contract 

## Base scene

```js
{
 id: "S1",
 stageId: "ST1",
 type: "interactive",
 title: "...",
 intro: "optional",
 objectiveIds: ["O1"],
 knowledge: { summary:"...", keyPoints:["..."], takeaway:"..." },
 content: {},
 actions: []
}
```

## Knowledge-first invariant

Substantial `concept`, `discussion`, `interactive`, and `pbl` scenes include a learner-visible `knowledge` block. The renderer places it before the interaction. The interaction should apply, test, manipulate or deepen what was just explained; it must not substitute for explanation.

## discussion

Explain the conceptual frame first. Then the learner commits, pre-generated role voices reveal, and synthesis/unresolved uncertainty closes the scene.

## interactive

```js
content: {
 widgetType: "diagram",
 widgetConfig: { kind: "knowledge-graph", ... },
 summary: "accessible fallback"
}
```

Read the matching `references/widgets/<widget>.md`.

## quiz / mastery

Use `references/assessment.md`. Each item has stable ID, objective ID, kind, prompt, deterministic answer rule, feedback and optional remediation mapping.

## pbl

```js
content: {
 learnerRole: "...",
 mission: "...",
 resources: [{ id:"R1", label:"...", text:"..." }],
 initialState: {},
 metricMeta: {},
 microtasks: [{ id:"T1", label:"...", doneWhen:"..." }],
 decisions: [{ id:"D1", label:"...", effects:{}, rationale:"..." }],
 milestones: [{ afterDecisions:2, prompt:"..." }],
 debrief: "..."
}
```

Consequences are deterministic and inspectable.

## reflection

Free-form response + delayed self-rubric/checklist. Never falsely AI-grade.

## exposition requirement

Before rendering the scene-specific interaction, substantial `orientation`, `concept`, `discussion`, `interactive`, and `pbl` scenes should provide a deep `knowledge` block. The renderer supports multi-paragraph sections, worked examples, comparison tables, boundaries, connections, glossary chips and self-check prompts. See `deep-explanation.md`.

Interaction controls must not be the learner's first exposure to a core concept. The current-page TOC is generated from authored knowledge subsections.


## equation payload

Equation steps should use structured `formula` objects (`mathml` + `tex`/spoken fallback) rather than plain `expression` strings. Knowledge exposition may use `definitionFormula`, `sections[].formula`, `sections[].formulas`, `workedExamples[].steps[].formula`, and `resultFormula`. See `math-typesetting.md`.


## textbook semantic payload

A substantial knowledge block may include `semanticBlocks`. Use stable IDs and the contracts in `textbook-semantics.md`. Formal named claims should be cross-referenceable; proof blocks link with `of`; exercises use `dependsOn` to point to already-taught statements. The semantic blocks render inside the reading layer before the scene-specific interaction.

## scene extensions

### Rich mathematical narrative

Knowledge prose may be an array of text/formula atoms. Formula atoms use native MathML plus fallback and are rendered in the normal reading flow.

### Animated diagram

`interactive/diagram` may declare `animation.enabled`, `animation.motion`, `animation.initialStep`, and `animation.interval`; diagram nodes/edges declare integer `step`. Playback is deterministic and local.

### Adjustable experiment

When `meta.experimentPolicy` is `adjustable-when-applicable`, relevant simulation/data-lab/quantity-lab/chemistry scenes should expose meaningful controls whose values affect a local deterministic result.

## native Pack scene notes

- Language native labs teach meaning/form/use and deterministic structure; accepted variants must be explicit.
- Humanities source comparison requires provenance, text status, context and shared comparison lenses; argument maps distinguish evidence from interpretation.
- Social Science causal DAGs expose assumptions and adjustment logic; evidence matrices expose design-specific inference limits.
- A final scene may surface an explicit session-feedback call to action. This is optional learner-entered feedback, not hidden analytics.
