# Source Coverage Inventory

Before generating a substantial source-based course, inventory what is actually present in the user's material.

## `sourceCoverage`

```json
{
 "sourceCoverage": {
 "status": "partial",
 "covered": ["8.1", "8.2", "8.3", "8.4", "8.5"],
 "omissions": ["8.6 is listed in the table of contents but absent from the uploaded PDF"]
 }
}
```

Never silently replace a missing scanned page, chapter, figure, proof, or exercise with model memory. Outside material may be used only when the user asked to expand/research and it must be clearly labeled as external.

## `contentInventory`

Each source-derived core concept should have a stable entry:

```json
{
 "id": "C-8.3",
 "label": "Simple solid surface area and volume",
 "importance": "core",
 "sourceLocator": "Chapter 8 §8.3",
 "sceneIds": ["S-83-CONCEPT", "S-83-LAB"],
 "exampleRefs": ["ex-831", "ex-832"],
 "practiceRefs": ["q-831", "q-832", "m-83a"],
 "explainBackRefs": ["S-83-EXPLAIN"]
}
```

For `meta.practicePolicy.mode="mastery-loop"`, strict validation checks that core inventory entries have:
- at least one teaching scene;
- the configured minimum number of worked examples;
- the configured minimum number of practice items;
- explain-back coverage when required.

This is a coverage contract, not a reason to pad a lesson. Combine tiny facts into one coherent concept when that better reflects the source.

## figure coverage

Geometry-native inventory entries may also declare:

```json
{
 "figureRefs": ["fig-83-net", "fig-83-scale"]
}
```

When `meta.figurePolicy.mode="geometry-native"`, strict validation resolves these IDs against actual `knowledge.pedagogicalFigures`. Figures therefore participate in source/course coverage instead of being an untracked visual afterthought.
