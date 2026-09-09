# Textbook Semantic Blocks

Use semantic blocks when the discipline teaches knowledge through named statements, derivations, proofs, canonical examples, or exercises. They are first-class course data, not decorative callouts.

## Supported block kinds

- `definition` — introduces a term/object/property precisely.
- `lemma` — supporting result used by a later claim.
- `theorem` — central formal result.
- `proposition` — result of narrower/local scope.
- `corollary` — result that follows quickly from a prior result.
- `proof` — justified argument linked with `of` to a theorem/lemma/proposition/corollary.
- `example` — worked application tied to prior statements.
- `exercise` — learner task with optional hint ladder and delayed solution.
- `remark` — nuance, convention, interpretation, or boundary.

Not every discipline needs theorem language. Use semantic blocks only when they improve the epistemic structure.

## Stable block shape

```js
{
 id: "thm-inverse-exists",
 kind: "theorem",
 number: "3.2",
 title: "模逆存在条件",
 statement: "整数 a 在模 n 下存在乘法逆元，当且仅当 gcd(a,n)=1。",
 formula: {
 tex: "a^{-1} \\pmod n \\text{ exists } \\Longleftrightarrow \\gcd(a,n)=1",
 spoken: "a has a multiplicative inverse modulo n if and only if gcd of a and n equals one",
 mathml: "<math display=\"block\">...</math>"
 },
 references: ["def-modular-inverse"]
}
```

Use globally unique semantic block IDs. Number/label should be stable for systematic courses so prose can say “由定理 3.2”.

## Proof contract

```js
{
 id: "proof-inverse-exists",
 kind: "proof",
 of: "thm-inverse-exists",
 strategy: "分别证明必要性与充分性，并使用 Bézout 恒等式。",
 steps: [
 { text: "假设逆元 x 存在。", formula: {...}, reason: "模逆定义" },
 { text: "因此存在整数 k 使 ax-kn=1。", formula: {...}, reason: "同余定义" },
 { text: "任意 a,n 的公因子都必须整除 1。", reason: "整除的线性组合封闭性" }
 ],
 conclusion: "因此 gcd(a,n)=1；反向由 Bézout 恒等式得到逆元。"
}
```

Rules:

1. One non-trivial inference per step.
2. State the justification, theorem, definition, algebraic rule, or evidence for each important transition.
3. Do not hide domain assumptions.
4. If a full proof is intentionally omitted, mark the claim with `proofRequired:false` and explain why, or provide `proofSketch`.
5. In a formal/quantitative course, a central theorem should not appear as an unsupported fact.

## Example contract

```js
{
 id: "ex-inverse-3-mod-7",
 kind: "example",
 number: "3.1",
 title: "求 3 在模 7 下的逆元",
 prompt: "找 x 使 3x ≡ 1 (mod 7)。",
 steps: [
 { text: "尝试 x=5。", formula: {...} },
 { text: "15 除以 7 余 1。", formula: {...} }
 ],
 result: "因此 3 的模 7 逆元为 5。",
 references: ["def-modular-inverse", "thm-inverse-exists"]
}
```

A worked example should expose reasoning, not just the answer.

## Exercise contract

```js
{
 id: "exr-inverse-4-mod-8",
 kind: "exercise",
 number: "3.1",
 prompt: "判断 4 在模 8 下是否存在逆元，并说明理由。",
 dependsOn: ["thm-inverse-exists"],
 hints: [
 "先计算 gcd(4,8)。",
 "再使用模逆存在条件。"
 ],
 solution: {
 text: "gcd(4,8)=4≠1，因此不存在逆元。"
 }
}
```

The solution is hidden initially. Hints reveal progressively. An exercise should normally depend on knowledge already taught, never introduce a required theorem for the first time.

## Cross references

Use `references` for explanatory links and `dependsOn` for prerequisite relations. The runtime resolves semantic IDs across scenes and can navigate to the referenced block.

Examples:

- theorem references a definition;
- proof `of` a theorem;
- corollary references theorem;
- example references definition/theorem;
- exercise depends on prior theorem/example.

## Discipline adaptation

- Mathematics / theoretical CS: use the full Definition → Lemma → Theorem → Proof → Example → Exercise chain where natural.
- Physics / engineering: use Definition / Proposition / Derivation / Example / Exercise; call empirical laws “law/model” in prose rather than falsely labeling them theorem.
- Statistics: distinguish definition, estimator/property, theorem/assumption, worked calculation, interpretation exercise.
- Humanities/social science: prefer `definition`, `example`, `remark`, evidence sections and discussion; do not force theorem labels on interpretive claims.
- Programming: definitions and invariants may be semantic blocks; proofs are appropriate for correctness claims, otherwise prefer code trace/tests.

## Visual rule

Semantic blocks should look like textbook structures: restrained side rule, typographic label, generous prose spacing, and minimal card chrome. Proofs are quieter than theorems; exercises are distinguishable but not game-like.
