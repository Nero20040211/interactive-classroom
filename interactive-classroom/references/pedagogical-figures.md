# Pedagogical Figures 

`pedagogicalFigures` are explanation-first visuals embedded inside a knowledge scene. They are not decorative images and do not count as a substitute for exposition, examples, practice, or proof.

## Direct figure binding

Worked examples may point to one of these figures with `figureRef`. The reference must resolve inside the same `knowledge` block; both Modern and portable place the figure inside the example rather than repeating it in a separate gallery. This keeps the visual next to the statement, steps, and conclusion that it explains.

```json
{
  "id": "ex-components",
  "visualNeed": "mechanical",
  "figureRef": "fig-components"
}
```

Use direct, offline SVG teaching templates for an object, comparison, mechanism, construction, or misconception. `motion-components` is the shared physics template for a trajectory with horizontal and vertical components. Do not use a mind map merely as a substitute for a direct object or process figure, and do not use a remote image URL in the learner runtime.

## Why they exist

Use a pedagogical figure when a learner is likely to fail because the verbal/symbolic description does not yet create the right mental representation. Typical jobs:

- **concept** — show what an object or relation is;
- **compare** — place confusable cases side by side;
- **step** — externalize a construction/projection/procedure;
- **reasoning** — show why a proof/causal step is useful;
- **misconception** — contrast a tempting visual inference with the actual condition.

## Core contract

```json
{
 "id": "fig-84-skew",
 "figureKind": "misconception",
 "title": "投影相交，不等于空间相交",
 "learningPurpose": "区分二维投影与真实空间位置关系",
 "caption": "判断空间直线关系前，先检查共面性与真实公共点。",
 "after": "mechanism",
 "template": "spatial-relations",
 "sourceRef": "src-textbook",
 "sourceLocator": "Chapter 8 §8.4",
 "highlights": ["先判断是否共面", "二维投影会丢失深度"]
}
```

Required in strict :

- stable `id`;
- `figureKind` in `concept | compare | step | reasoning | misconception`;
- non-empty `title`, `learningPurpose`, and `caption`;
- supported `template` or an explicitly allowed Pack renderer;
- if `sourceRef` is present it must resolve to a declared source.

## Placement

Figures should appear **inside the explanation flow**, not in a gallery at the end. `after` supports:

- `prerequisites`
- `mentalModel`
- `intuition`
- `definition`
- `mechanism`
- `section:<section id or title>`
- `examples`
- `pitfalls`

If omitted, place after `mechanism`.

## Mathematics geometry templates

The Mathematics Pack currently provides:

- `solid-family` — compare common polyhedra/solids by structure;
- `oblique-projection` — show the staged logic of an oblique/axonometric sketch;
- `surface-net` — connect a solid to an unfolded surface decomposition;
- `spatial-relations` — compare intersecting/parallel/skew relations without trusting projection appearance;
- `bridge-line` — visualize the line-in-plane "bridge" used in parallelism reasoning;
- `generic-flow` — a bounded fallback for a small labelled reasoning chain.
- `motion-components` — a direct mechanics figure showing trajectory, position axes, and component vectors.

These diagrams are schematic teaching representations. They must not claim metric accuracy unless the renderer actually preserves it.

## Geometry quality gate

For `meta.figurePolicy.mode="geometry-native"` and a core Mathematics geometry inventory item:

- at least `minFiguresPerCore` figures (default 2);
- at least one **representation-building** figure: `concept | step | reasoning`;
- at least one **disambiguation** figure: `compare | misconception`;
- `contentInventory[].figureRefs` must resolve to real figure IDs.

A figure is not enough by itself: the surrounding prose must explicitly tell the learner what to notice and what cannot be inferred from the drawing.

## Feedback export

Figure-specific feedback may be exported with types:

- `figure-helpful`
- `figure-confusing-or-missing`

Promote a single observation to a Pack rule only after it is reproducible/generalizable and backed by a regression fixture.
