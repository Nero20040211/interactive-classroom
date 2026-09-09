# Native Math Typesetting Contract

Use browser-native **MathML Core** for substantive mathematical notation. The goal is textbook-quality offline rendering without CDN scripts or bundled font files.

## Formula object

```js
{
 tex: "a \\equiv b \\pmod n",
 spoken: "a is congruent to b modulo n",
 label: "式 2.1",
 mathml: "<math display=\"block\"><mi>a</mi><mo>≡</mo><mi>b</mi><mrow><mo>(</mo><mo>mod</mo><mi>n</mi><mo>)</mo></mrow></math>"
}
```

- `mathml` is the primary visual representation.
- `tex` is a source/fallback string, not the primary renderer.
- `spoken` or `ariaLabel` explains the formula accessibly.
- `label` is optional for equation numbering.

## Required use

Use MathML for fractions, roots, powers/subscripts, sums/integrals, matrices/tables, congruences, probability expressions, vectors, limits, derivatives, chemical/physical equations when symbolic structure matters, and every step in an `equation` derivation.

Simple variable names in ordinary prose may remain text. Do not convert every isolated `x` into MathML.

## Authoring rules

1. Define symbols before the first major display formula.
2. Pair a formula with prose explaining its meaning and why it is relevant.
3. In derivations, one nontrivial transformation per step plus a reason.
4. Keep assumptions/domain restrictions visible.
5. For long equations, split into semantic steps rather than shrinking type.
6. Provide `tex`/spoken fallback for every important display formula.
7. Never use `<pre>`, `<code>`, or monospace styling as the main mathematical presentation.

## Strict offline rule

Do not load KaTeX, MathJax, remote webfonts, or CDN assets in strict offline mode. Native MathML Core is the canonical renderer; formula source remains visible as a fallback/debug aid.


## Proof integration

When formulas participate in a theorem proof, place them inside `knowledge.semanticBlocks[kind="proof"].steps[].formula`. Each non-trivial symbolic transition should have an adjacent `reason`; MathML layout is not a substitute for logical justification.

## Operator typography

Use upright operator names and explicit spacing for textual mathematical operators. For example, render `mod`, `gcd`, `sin`, `cos`, `ln` as `<mtext>` or `mathvariant="normal"` operator text, and add `<mspace>` where needed. Do not concatenate visual text such as `modn` or mix English prose like “exists” into a symbolic display when a clearer symbolic statement is available.

## : formulas embedded in prose

Read `math-richtext.md`. Substantive equations/inequalities may no longer be authored as plain narrative strings. Use structured MathML formula atoms even when the formula occurs between explanatory paragraphs.
