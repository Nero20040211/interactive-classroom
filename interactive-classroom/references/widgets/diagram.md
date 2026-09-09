# Widget: diagram

Kinds:
- `whiteboard`
- `knowledge-graph`
- `timeline`
- `flow`
- `argument-map`
- `state-machine`

Required:
- stable element IDs;
- relationship semantics/labels;
- text summary;
- selectable details for dense diagrams;
- keyboard alternative to drag where drag exists;
- reset if layout/state is user-modifiable.

Do not use a generic graph when real geographic/image/spatial evidence is required.

## staged explanation

Use `animation.enabled` plus per-node/per-edge `step` values when a process is best learned progressively. Provide next/play/pause/replay controls through the canonical runtime. See `../animated-explanations.md`.
