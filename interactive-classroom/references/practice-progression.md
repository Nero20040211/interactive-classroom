# Practice Design — Example Diversity + Practice Progression

 keeps the mastery loop but makes the ladder verifiable instead of merely counting questions.

## Per-core default

For each `importance: core` inventory item:

1. **Worked Example A — standard**: canonical application with complete reasoning.
2. **Worked Example B — contrast/boundary**: changed representation, common misconception, or edge condition.
3. **Guided practice**: hint ladder available.
4. **Independent practice**: no answer-revealing scaffold before an attempt.
5. **Transfer practice**: changed context/representation/structure.
6. **Cumulative retrieval**: after several concepts, mix old and new objective IDs.
7. **Explain-back**: reconstruct the idea from memory and repair the first gap.
8. **Independent mastery gate**: at least two novel-transfer items per objective; all required items must pass when `requireTwoNovelTransfers:true`.

## Example contract

Worked examples should declare `variantType` when `requireExampleContrast:true`:

- `standard`
- `contrast`
- `boundary`
- `misconception`
- `reverse`

Two examples with the same algebra and only different numbers do not satisfy example diversity.

## Practice progression contract

When `requirePracticeProgression:true`, every core inventory item must reference practice whose `practiceLevel` covers:

- `guided`
- `independent`
- at least one of `transfer | retrieval`

This is checked from the actual referenced items, not inferred from scene titles.

## Hint discipline

Use progressive hints:

1. point to the relevant condition/representation;
2. state the principle without the concrete answer;
3. bottom out only when necessary, then require a why/explain-back.

## Error-analysis preference

Where useful, include an item asking for the **first invalid inference** in a plausible wrong solution. This is often more diagnostic than another isomorphic calculation.
