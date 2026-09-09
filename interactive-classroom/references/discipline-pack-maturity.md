# Discipline Pack maturity matrix

- **validated-native**: the Pack has discipline-native interaction contracts, strict static validator rules, and bundled regression evidence. Browser/runtime smoke remains a target-environment check when the interaction depends on browser behavior.
- **core-compatible**: the core can teach the discipline well, but no dedicated native-lab maturity claim is made.

| Pack | Status | validated native focus |
|---|---|---|
| mathematics | validated-native | geometry-lab, solid-geometry-lab, space-geometry-lab, pedagogical figures, MathML/proof practice |
| physics | validated-native | fbd-lab, circuit-lab, motion-lab, quantity-lab |
| chemistry | validated-native | molecule-lab, chemistry reaction lab, content-fit particle animation |
| biology | validated-native | genetics-lab, process/annotation support |
| ml-ai | validated-native | search-tree-lab, ml-boundary-lab, proof/data labs |
| statistics | validated-native | stats-lab, data-lab, random-trial-lab |
| computer-science | validated-native | data-structure-lab, recursion-lab, complexity-lab, deterministic code trace |
| geography | validated-native | verified map-lab plus spatial reasoning |
| language | validated-native | cloze-lab, sentence-builder-lab, grammar-tree-lab |
| humanities | validated-native | source-comparison-lab, argument-map-lab |
| social-science | validated-native | causal-dag-lab, evidence-matrix-lab |
| procedural-vocational | core-compatible | procedural-skill, PBL, checkpoints and safety boundaries |

A static maturity claim does not pretend that every subfield or browser environment is covered. Listening/pronunciation still needs real media or a speech engine; image-heavy humanities may need supplied media; specialized statistics/econometrics may need additional model-specific labs. Run browser smoke in the target Codex environment when the generated course relies on gesture, WebGL, layout, or actual modern-runtime bundling.
