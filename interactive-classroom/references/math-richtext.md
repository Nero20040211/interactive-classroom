# Strict Math-in-Prose Contract 

 closes a loophole from earlier releases: a course could use excellent MathML in formal equation widgets while still hiding substantive equations inside ordinary prose strings. That is no longer acceptable in strict mode.

## Rule

If a learner is expected to parse a symbolic equality, inequality, congruence, summation, fraction, limit, integral, matrix relation, or model equation, author it as a structured formula object.

Do not write this inside a normal string:

```text
K=1/2 mv²
ŷ=β₀+β₁x
MSE=(1/n)Σ(...)
h(n)≤h*(n)
```

Instead use a formula atom:

```json
{
 "text": "经典动能由下式定义：",
 "formula": {
 "tex": "K=\\frac12 mv^2",
 "spoken": "动能 K 等于二分之一 m v 平方",
 "mathml": "<math display=\"block\">...</math>"
 }
}
```

## Rich narrative atoms

Narrative fields such as `mentalModel`, `intuition`, `mechanism`, `section.body`, and selected list items may be arrays that interleave prose and formula atoms:

```json
"mechanism": [
 {"text": "先写预测模型：", "formula": {...}},
 {"text": "再用损失衡量预测误差：", "formula": {...}},
 {"text": "最后解释参数改变为何改变损失。"}
]
```

A compact inline formula may use:

```json
{
 "parts": [
 {"text": "当 "},
 {"formula": {...inline MathML...}},
 {"text": " 时，关系成立。"}
 ]
}
```

Use inline mathematics only for genuinely short relations. Major equations and every derivation step should remain display mathematics.

## Validation

For current schema, strict validation:

- rejects formula-like equations leaked into narrative strings;
- rejects any declared `formula`, `definitionFormula`, `resultFormula`, `promptFormula`, or `formulas[]` entry that lacks MathML plus a text/TeX/spoken fallback;
- keeps metadata such as physical dimensions or internal IDs out of the prose leakage heuristic.

The goal is not to turn every single variable name into a formula block. The goal is to ensure that **substantive symbolic statements are typeset as mathematics rather than disguised as ordinary text**.
