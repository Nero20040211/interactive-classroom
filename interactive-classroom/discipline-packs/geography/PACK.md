# 地理 Discipline Pack

Pack ID: `geography`

Status: **validated-native**

## Native learning language

Preferred: `map-lab`, data-lab, diagram/animation and source-backed spatial comparison. A substantial map lesson should teach coordinate system, projection/scale limits, spatial pattern and an interpretation task — not just put pins on a map.

## Required integrity

- Every map layer is embedded and has provenance.
- Stable points/features have IDs and source references.
- State `coordinateSystem`, `projection`, `scaleNote`, and whether boundaries are omitted/schematic.
- Administrative/political boundaries need `boundaryPolicy`; never invent or silently alter disputed geometry.
- Distance work uses great-circle distance for global point comparison, not pixel distance.
- Separate observation (where things are) from explanation (why the pattern occurs).

## Native regression

The bundled regression suite validates verified coordinates, projection/scale disclosure, provenance, spatial comparison, and process-to-map reasoning. Strict gates reject invalid longitude/latitude and undeclared geographic sources.


## animation profile

Prefer water/air/plate/vector primitives; motion must encode spatial direction, reservoir transfer, scale, or Earth-system process.
