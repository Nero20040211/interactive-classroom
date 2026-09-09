# Scroll & Interaction State Contract

A learning page must not unexpectedly teleport the learner to the document top.

## Rules

1. **In-scene interactions preserve viewport position.** Quiz answers, dialogue reveal, graph-node selection, timeline selection, hints, PBL decisions, equation steps, code steps and teacher actions may re-render scene HTML, but must restore the previous `window.scrollY`.
2. **Drag never re-renders the whole scene.** Knowledge-graph pointer movement updates SVG node/edge attributes in place.
3. **Scene navigation scrolls to the new scene heading, not to page top.** `上一页 / 下一页` and left-navigation clicks use the stage heading as the scroll target.
4. **Current-page TOC scrolls to a subsection anchor without scene re-render.**
5. **Preserve state across re-render:** selected nodes, quiz answers, dialogue progress, reflections, simulation parameters, PBL state and guide state remain in the runtime state object.
6. Respect reduced-motion preferences: use immediate scrolling when reduced motion is enabled.

## Regression checks

- Scroll halfway down a long explanation, click a knowledge-graph node: vertical position should stay effectively unchanged.
- Drag a knowledge-graph node: no page jump.
- Click “下一页”: land at the next scene heading; the course header need not be re-shown.
- Reveal a dialogue line / hint / quiz feedback: remain at the current learning location.
- Click a current-page TOC item: move to that subsection only.
