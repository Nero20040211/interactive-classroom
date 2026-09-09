# Adjustable Experiment Contract 

The practice area should prefer **learner-controlled experiments** over fixed demonstrations whenever the concept contains meaningful parameters or quantities.

The default experiment loop is:

**predict → change one variable → observe → compare → explain → reset/try another combination**

## Experiment identity and deduplication

Do not add several prompts that ask the learner to perform the same control-variable comparison. Give each experiment a stable `experimentKey` and an instructional `experimentRole`, then state the variables that change, the variables held constant, and the evidence question:

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

Keys are unique within a course. Exact duplicate prompts are invalid even when their wording is stored in different experiment arrays. Set `meta.experimentDedupPolicy:"stable-key"` when using structured entries; the strict validator then requires both `experimentKey` and `experimentRole` while legacy string prompts remain readable in older courses.

## `meta.experimentPolicy`

For courses where adjustable experiments are broadly appropriate, set:

```json
"experimentPolicy": "adjustable-when-applicable"
```

This does not force sliders into non-quantitative scenes. It tells the planner and validator that simulations/data labs/quantity labs/chemistry labs should expose learner control when a deterministic model exists.

## Simulation

Use existing `parameters[]` with visible assumptions and guided experiment prompts.

## Data Lab

 supports learner-controlled parameter overlays. Canonical linear-regression configuration:

```json
{
 "widgetType": "data-lab",
 "widgetConfig": {
 "experimentRequired": true,
 "model": {"kind":"linear-regression"},
 "parameters": [
 {"id":"beta0","label":"截距 β₀","min":0,"max":100,"step":1,"initial":50},
 {"id":"beta1","label":"斜率 β₁","min":-10,"max":10,"step":0.25,"initial":3}
 ]
 }
}
```

The runtime updates the fitted line and MSE locally without a scene re-render.

## Quantity Lab

Quantities can declare:

```json
{"id":"m","adjustable":true,"min":1,"max":10,"step":0.5}
```

A deterministic local model is required. Canonical registry in includes:

- `kinetic-energy`;
- `momentum`;
- `density`;
- `ohms-law`.

The derived quantity updates live while units/dimensions remain explicit.

## Chemistry

For balancing practice:

```json
"adjustableCoefficients": true
```

The learner changes **stoichiometric coefficients only**. Compound subscripts remain fixed. Atom-count feedback recalculates from structured compound data.

## Validation

In strict , when an adjustable experiment is declared/required:

- simulations need at least one parameter;
- data labs need parameters and a deterministic supported model;
- quantity labs need at least one adjustable quantity and a local computation model;
- chemistry balancing labs need adjustable coefficients;
- parameter manipulation must remain deterministic/offline.

Do not expose controls with no causal effect. Every control must visibly change a result, graph, state, metric, or conservation check.
