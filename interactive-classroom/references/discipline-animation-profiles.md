# Discipline Animation Profiles 

| Pack | Preferred profiles | Preferred primitives / native labs | Reject when |
|---|---|---|---|
| mathematics | `mathematics-probability`, `mathematics-dynamic-quantity`, `mathematics-geometry` | die, coin, sample-point, math-point, vector, geometry labs | motion does not encode a mathematical state |
| statistics | `statistics-probability`, `statistics-sampling` | coin, die, sample-point, random-trial-lab | frequency is shown becoming exactly constant |
| physics | `physics-motion`, `physics-force`, `physics-field`, `physics-wave` | projectile, projection-marker, vector, motion/fbd/circuit labs | object moves without relevant time/vector state |
| biology | `biology-cellular-process`, `biology-genetics`, `biology-system` | molecule, energy-token, genetics lab | flowchart rectangles replace biological entities |
| chemistry | `chemistry-reaction`, `chemistry-particle`, `chemistry-electrochemistry` | molecule, ion, electron, vector | atom/charge/particle meaning is hidden |
| computer-science | `computer-science-runtime`, `computer-science-algorithm`, `computer-science-data-structure` | stack-frame, array-cell, pointer, recursion/search labs | motion disagrees with execution state |
| geography | `geography-earth-system`, `geography-flow`, `geography-spatial-change` | water-drop, air-mass, plate, vector, map-lab | arrows do not encode a spatial/process relation |
| ml-ai | `ml-ai-optimization`, `ml-ai-search`, `ml-ai-decision` | search-tree-lab, ml-boundary-lab, vector | objective/state change is omitted |
| language | `language-production` only when sequence matters | sentence-builder, grammar-tree | grammar labels move without improving form/meaning/use |
| humanities | `humanities-chronology` sparingly | source-comparison, argument-map | motion implies causality unsupported by evidence |
| social-science | `social-science-data-generating` when assumptions are explicit | causal-dag, evidence-matrix | model arrows are presented as observed causal proof |
| procedural-vocational | `procedural-vocational-sequence` | procedural-skill | cinematic motion sacrifices safety/step precision |
