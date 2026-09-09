# Widget: equation

Use for formulas, derivations, proofs and worked mathematical transformations.

Use native MathML Core as the primary renderer for substantive formulas. Include `tex`/spoken fallback; do not require a CDN, MathJax, KaTeX, or bundled math fonts.

Required:
- define notation;
- show premise/goal;
- ordered derivation/proof steps with reason for each step; Modern reveals these steps one at a time with a visible progress state and reset control;
- learner predicts/selects the next step at least once when useful;
- expose assumptions/domain restrictions;
- text fallback for formulas.

Modern's progressive reveal is a learning aid, not a hidden answer gate: the full ordered step list remains in the offline course data, and the portable renderer keeps the same steps inspectable. When `nextStepPrediction` (or the legacy `prediction`) declares options, render one local choice-and-feedback checkpoint before the next derivation step. Reduced motion removes interpolation but keeps the discrete steps and controls.

Do not skip nontrivial algebraic/logical steps simply for visual neatness.

See `../math-typesetting.md`. Formula steps should use `{formula:{mathml,tex,spoken,label}, reason}` rather than plain expression strings.
