# Deep Explanation Contract

The classroom must be able to teach the topic without requiring the learner to search elsewhere for every missing connective step. Interactions reinforce exposition; they do not replace it.

## Default depth profile

For ordinary natural-language requests such as “我要学习密码学”, default to **learn-deep** unless the user explicitly asks for a quick overview.

- `overview`: 250–500 Chinese characters (or ~150–300 English words) per major concept scene.
- `learn-deep` (default): 700–1400 Chinese characters (or ~450–900 English words) per major concept scene when the concept is substantial.
- `systematic/deep`: 1200–2200 Chinese characters (or ~750–1400 English words) per major concept scene, split across readable subsections.

These are design targets, not quotas. A simple concept may be shorter; a difficult proof/mechanism may be longer. Never pad with repetition.

## What a substantial explanation should contain

Use the subset that fits the discipline, but normally cover at least four of these before assessment:

1. **Prerequisite connection** — what prior idea this depends on.
2. **Mental model / intuition** — what problem the idea solves and how to picture it.
3. **Precise definition / mechanism** — formal statement, notation, variables, assumptions, or interpretive claim.
4. **Reasoning chain** — why it works; causal chain, derivation, proof sketch, algorithm trace, or evidence logic.
5. **Worked example(s)** — at least one non-trivial example for a central concept; two for difficult concepts.
6. **Contrast / boundary** — what it is not, when it fails, and nearby concepts that are easy to confuse.
7. **Connection forward** — how this concept is used by the next concept.
8. **Self-check** — one or two questions learners should be able to answer before moving on.

## Course-level depth

For a broad topic-only request:

- identify 4–8 core concepts rather than attempting a shallow encyclopedia;
- include prerequisites before advanced material;
- allocate at least one exposition scene and one practice/assessment opportunity to every declared objective;
- use 6–12 scenes for a normal course, more only when the topic truly requires it;
- do not introduce important facts only inside quiz feedback.

For formal/quantitative topics, show intermediate steps instead of jumping from formula to result. For programming, explain the execution model before tracing code. For humanities, include context, claim, evidence, alternative interpretation, and boundary. For experimental subjects, explain variables, units, model assumptions, measurement limits and interpretation before simulation.


## Textbook semantic layer

For formal or theorem-driven topics, narrative depth alone is not enough. Use `knowledge.semanticBlocks` so the learner can see the epistemic role of each statement:

**Definition → supporting Lemma/Proposition → Theorem → Proof → Worked Example → Exercise → Remark/connection**

Use only the subset that is natural. Do not duplicate the same definition verbatim in both `definition` prose and a semantic definition block. The semantic chain should clarify dependency, not inflate length. See `textbook-semantics.md`.

## Knowledge schema extensions

A `knowledge` block may use:

```js
knowledge: {
 title: "...",
 summary: "...",
 prerequisites: ["..."],
 mentalModel: "multi-paragraph prose",
 intuition: "multi-paragraph prose",
 definition: "multi-paragraph precise statement",
 mechanism: "reasoning chain",
 keyPoints: ["..."],
 sections: [
 { title: "为什么", body: "..." },
 { title: "推理链", body: "...", bullets: ["..."] },
 { title: "公式", body: "...", formula: { tex: "...", spoken: "...", mathml: "<math ...>...</math>" } }
 ],
 semanticBlocks: [
 { id: "def-1", kind: "definition", number: "1.1", title: "...", body: "..." },
 { id: "thm-1", kind: "theorem", number: "1.1", statement: "...", references: ["def-1"] },
 { id: "proof-1", kind: "proof", of: "thm-1", steps: [{ text: "...", reason: "..." }] },
 { id: "exr-1", kind: "exercise", prompt: "...", dependsOn: ["thm-1"], hints: ["..."], solution: "..." }
 ],
 workedExamples: [
 { title: "例 1", text: "...", visualNeed: "mechanical", figureRef: "fig-example-1", steps: [{ text: "...", formula: { mathml: "<math>...</math>", tex: "...", spoken: "..." }, reason: "..." }], result: "...", resultFormula: { mathml: "<math>...</math>", tex: "...", spoken: "..." } }
 ],
 comparison: {
 headers: ["概念", "目标", "关键差异"],
 rows: [["A", "...", "..."]]
 },
 evidence: "...",
 boundaries: ["..."],
 pitfalls: ["..."],
 connections: ["..."],
 glossary: [{ term: "...", definition: "..." }],
 checkYourself: ["..."],
 takeaway: "..."
}
```

Do not mechanically fill every field. Choose fields that complete the learner's reasoning chain.

For spatial, mechanical, structural, or process examples, prefer a direct offline pedagogical figure bound with `figureRef` over a text-only example or a mind-map-like diagram. The figure should sit beside the statement and derivation so the learner can inspect the object or relationship while reading the steps. A figure is not a substitute for the explanation or the calculation.

## formula-depth rule

In formal or quantitative scenes, prose depth and symbolic depth are both required. A long paragraph cannot substitute for missing derivation steps, and a formula cannot substitute for explanation. Use native MathML Core for major equations and explain each transformation in prose.

In Modern Runtime, derivation steps are intentionally revealed one at a time with a visible reason and optional assumption. Keep the complete step list in the course data so reduced-motion users and the portable fallback can inspect the same reasoning chain; do not jump straight from a target formula to a result.

## explanation + mathematics

A deep explanation is not allowed to become typographically shallow. If a reasoning paragraph reaches an actual equation or inequality, break the narrative at that point and render the relation as a structured formula atom. Then continue with prose explaining what changed and why. This creates a readable sequence of **claim → formula → interpretation**, rather than burying symbolic work inside long sentences.
