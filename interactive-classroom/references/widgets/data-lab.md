# Widget: data-lab

Use for statistics, experimental results, empirical social science, economics and data reasoning.

Required:
- dataset/source/provenance note when available;
- variables and units;
- visible table or bounded sample;
- chart appropriate to the question (`scatter`, `bar`, `line`);
- deterministic summary calculation if used;
- interpretation prompt;
- distinguish description from causal inference.

Never fabricate data and present it as observed. Label synthetic/illustrative data explicitly.

## adjustable model overlay

For parameter-learning tasks, set `experimentRequired:true`, declare `parameters[]`, and use a deterministic local model. The canonical shell currently supports `model.kind="linear-regression"` with live fitted-line and MSE updates. See `../interactive-experiments.md`.
