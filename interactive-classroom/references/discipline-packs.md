# Discipline Packs

Discipline Packs sit between the generic Discipline Router and scene generation. The core owns pedagogy, reader UI, offline runtime, MathML, citations, assessment honesty and state management. Packs own subject conventions and native interaction choices.

## Routing contract

1. Infer `meta.discipline.primary`.
2. Select `meta.disciplinePack` from the canonical pack IDs.
3. Load only that pack plus justified secondary packs.
4. Build the outline using the pack's preferred widgets and misconceptions.
5. Run core validator + pack-specific gates.

A substantial course should not omit `meta.disciplinePack`. Cross-disciplinary courses may add `meta.secondaryPacks` (max 2).

## Maturity rule

A pack is not considered mature merely because the core can render prose. A pack should have: routing guidance, notation/convention rules, at least one native interaction, validator rules, a positive fixture and a negative test.

## Geographic integrity

`map-lab` accepts only embedded coordinates/polygons/GeoJSON with provenance. If local geography is unavailable, use an explicitly labeled schematic diagram instead of inventing a map.


## Native maturity coverage

Computer Science and Geography use stateful algorithm/data-structure labs and verified spatial reasoning respectively. Language uses deterministic context/form construction labs; Humanities uses source comparison and argument structure with provenance/context gates; Social Science uses causal DAG adjustment reasoning and evidence-design matrices. See `discipline-pack-maturity.md` for the current static maturity matrix and target-environment smoke boundary.

The core may export explicit learner session feedback. Pack/core mutation is outside the teaching Skill and belongs to the separate `interactive-classroom-refiner` workflow.

## explanation figures

Discipline Packs may supply subject-specific pedagogical-figure templates while the core owns the common figure contract. Mathematics currently validates geometry figures; other Packs should only promote figure templates after a subject-specific regression demonstrates that the visual encodes a real learning relation rather than decoration.
