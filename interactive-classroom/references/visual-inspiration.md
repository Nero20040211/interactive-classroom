# Visual Inspiration — Learning / Documentation Style

The canonical HTML should feel like a calm textbook + documentation reader, not a dashboard or marketing landing page.

Reference patterns (inspiration only; do not copy source code):

- **Astro Starlight** — global sidebar plus current-page table of contents; responsive sidebars; headings as navigation anchors.
- **Nextra docs** — restrained documentation chrome, readable content column, structured navigation, callouts and code-oriented teaching.
- **Just the Docs** — few dependencies, mobile-first documentation, “make the content shine”.
- **paper-to-course** — warm off-white learning surface, intuition-before-formalism, sidebar/progress, code/math blocks, chapter-like modules.
- **frontend-textbooks** — editorial reading rhythm, typography hierarchy, page pacing, diagrams and skim-worthy exhibits.

## Adopted principles

1. **Content is the visual center.** Do not wrap every paragraph in a card.
2. **Three-layer navigation on wide screens:** course outline (left), reading page (center), current-page outline (right).
3. **Editorial reading width:** ~720–820 px for prose, with wider interactive canvases only when necessary.
4. **Warm paper surface + restrained accent.** Prefer neutral backgrounds and one quiet accent over gradients/glows.
5. **Hierarchy through spacing and typography**, not boxes everywhere.
6. **Examples, warnings and takeaways are localized callouts**, while normal exposition remains plain reading content.
7. **Code/math gets a distinct high-contrast surface**; body prose stays comfortable for long reading.
8. **Interactions appear after the explanation** in a clearly separated “练习与交互” area.
9. **Current-page TOC** is generated from explanation subsections and scrolls to them without re-rendering.
10. **Responsive collapse:** hide page TOC first, then turn the course sidebar into a horizontal strip on narrow screens.

## Avoid

- giant gradient hero cards;
- excessive shadows and nested cards;
- dashboard metric styling for ordinary explanations;
- text walls with no subsection rhythm;
- decorative animation unrelated to learning;
- layout changes that reset the learner's scroll position.

## GitHub style study

For the visual maintenance pass, also read `visual-style-sources.md`. The shell was reviewed against Tufte CSS, Simple.css, Pico CSS, Just the Docs, and Primer CSS patterns. The adopted result is not a framework import: it is a local design system emphasizing editorial measure, quiet navigation, semantic tokens, responsive controls, and explicit foreground/background color pairs for animation labels.

Additional rules:

- A process animation may use an internally scrollable canvas on narrow screens rather than shrinking 15–18 px labels into unreadable text.
- Do not use a single global text color on differently colored animation actors. Each actor semantic role must resolve to an explicit `background + stroke + label text` palette.
- Target at least 4.5:1 contrast for normal actor labels and 3:1 for important graphical outlines against the animation canvas.
- Color never carries the only meaning: keep labels, shape/state changes, and step captions.
