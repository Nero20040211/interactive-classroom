# Visual System — Textbook Reader

Use this reference for full classroom generation or visual revisions.

## Principle

The page should read as a **calm textbook/documentation reader with interactive practice**, not a generic admin dashboard, marketing landing page, or collection of utility cards. Knowledge explanation is the visual anchor; interaction is the practice layer. Visual hierarchy must communicate:

1. where the learner is;
2. who is speaking;
3. what concept/decision is active;
4. what changed because of the learner's action;
5. what to do next.

Do not imitate a third-party product pixel-for-pixel. Use an original, restrained classroom visual language.

## Canonical layout

Desktop:

- `classroom-bar`: title, offline state, progress, reset;
- `role-strip`: compact identities for Teacher / peers active in this course;
- three-column body on wide screens:
 - course/scene navigator;
 - editorial reading stage;
 - current-page knowledge outline generated from explanation subsections;
- inside stage, allow a split only when the visual truly needs it (e.g. dialogue + whiteboard).

Mobile:

- single column;
- scene navigation becomes horizontal/local scroll or compact select;
- role strip wraps;
- visual canvases fit width;
- no page-level horizontal overflow.

## Role avatars

Default to CSS/inline SVG/initials. A role identity needs:

- stable role ID;
- visible name;
- short function label;
- avatar mark/initial;
- optional `tone` token used only for subtle distinction.

Never imply a role is live when the content is pre-generated. Useful microcopy: “课堂角色 · 内容已预生成”.

## Dialogue

Dialogue scenes should support:

- learner commitment before reveal;
- one bubble at a time or staged reveal;
- `下一条` / `全部展开` controls;
- optional `重新播放`;
- final synthesis only after viewpoints;
- `prefers-reduced-motion` disables entrance animation but not content.

Avoid timed autoplay as the only path. User control beats theatrical pacing.

## Whiteboard

Use SVG when relationships/sequence matter. Minimum:

- semantic title/summary outside SVG;
- labeled nodes/shapes;
- arrows/links with clear meaning;
- selected element detail panel when dense;
- progressive reveal only if it supports explanation;
- visible legend for encoded categories.

Do not use decorative handwritten effects that reduce readability.

## Knowledge graph

Required behavior for draggable graphs:

- nodes are `<g>` or equivalent focusable interactive elements;
- pointer drag with constrained bounds;
- arrow keys move focused node in small increments;
- reset layout control;
- selecting a node persistently shows definition/details;
- edge labels or legend when relation types differ;
- graph has a text fallback/list of relations.

Do not make drag necessary to understand the content.

## Timeline / process map

- preserve chronological/process order;
- event markers are buttons or keyboard-focusable;
- selected event remains visually distinct;
- details update in a dedicated panel;
- allow process timelines that are not literal dates, but label them as stages.

## Simulation

Visual composition:

- prompt/prediction at top;
- parameter controls with current value and units;
- output visualization;
- concise interpretation that updates with the model;
- assumptions/model limits;
- guided experiment prompts.

Do not animate continuously unless motion itself communicates the modeled process. Always provide pause/stop for continuous animation.

## PBL

Use a decision-room pattern:

- learner role + mission;
- current state metrics;
- evidence/resource snippets;
- decision controls;
- immediate deterministic consequence;
- decision log;
- debrief after a meaningful milestone.

Never hide scoring logic if the score affects feedback.

## Color and typography

- use system fonts only by default;
- high contrast text;
- neutral surfaces;
- one accent for active controls/selection;
- distinct role colors only when needed, and never color-only identification;
- avoid neon/glow-heavy “AI” aesthetics.

## Motion

Allowed:

- dialogue bubble entrance;
- subtle connector/node transitions;
- progress transitions;
- outcome change emphasis.

Avoid:

- constant ambient motion;
- bouncing avatars;
- fake typing spinners;
- animation that delays access to content.

## Accessibility

- all primary actions reachable by keyboard;
- visible focus ring;
- `aria-live` for status/feedback, not for large scene rerenders;
- SVG carries `role="img"` or interactive semantics plus text summary;
- touch targets ~44 px where practical;
- no essential hover-only state.


## Knowledge-first visual hierarchy

Every core scene should visibly separate:

1. **知识讲解** — the main explanatory block;
2. **动手理解** — widget/discussion/decision/practice;
3. **反馈与带走** — debrief/takeaway.

The knowledge block should feel like authored course material: comfortable line length, meaningful section labels, clear examples, restrained callouts and a prominent takeaway. Do not hide the explanation behind accordions.

## Aesthetic direction

- Use a subtle layered page background and elevated central learning surfaces;
- use generous 18–24 px internal spacing on desktop;
- use restrained radii/borders and minimal shadow; normal prose should not be wrapped in separate cards;
- keep accent color concentrated on navigation, active controls and learning emphasis;
- give the course header a clear identity without recreating a product chrome;
- use small semantic icons/initials drawn with CSS/text, never remote assets by default;
- use scene-type labels in learner language (e.g. “概念讲解”, “互动实验”, “掌握检测”) rather than raw internal enum names;
- group scene navigation by Stage where possible.


## reader notes

See `visual-inspiration.md` for the documentation/textbook references and `scroll-state-contract.md` for navigation behavior. The explanation column is primary; interactive canvases may widen beyond it only when a diagram/simulation needs space. On wide screens the current-page TOC should remain secondary and quiet.

## textbook math and reading polish

Use native MathML display blocks with generous vertical rhythm. Major equations belong in the reading column, not code-style boxes. Keep formula labels subtle, reasoning text immediately below the equation, and avoid dense dashboard decoration around exposition.


## semantic typography

Definition/theorem/proof/example/exercise blocks use restrained textbook side rules and typographic labels, not dashboard cards. Proof blocks should be visually quieter than theorem statements; exercises should be distinct but not game-like. Stable numbers/labels support references such as “定理 3.1”. The current-page outline may include semantic block headings and should mark the subsection currently in view.

## reader-first visual refinement

The HTML shell now treats visual polish as part of pedagogy, not decoration.

### Reading surface

- Keep the main explanatory measure near 760 px; let only labs/figures widen.
- Use generous paragraph leading and whitespace before adding cards.
- Preserve a warm/light paper surface in light mode and a neutral low-glare surface in dark mode.
- Use serif selectively for major editorial headings, system sans-serif for body/UI, and system monospace for code.
- Tables and long strings must remain usable on small screens without page-level horizontal overflow.

### Animation palette

Process actors use seven semantic palettes: `primary`, `secondary`, `accent`, `good`, `warn`, `muted`, `container`.

Each palette has independent `bg`, `stroke`, and `text` tokens in light and dark themes. Do not derive label text from the global `--text` token. Run `scripts/audit_visual_style.py` before release.

### Mobile animation readability

Do not scale a 760 px process diagram down to a 350 px viewport if doing so makes labels unreadable. The canonical strategy is `scroll-inside`: the process canvas remains roughly 680 px wide inside an overflow container, while the page itself remains free of horizontal overflow.

### Visual coding

Never rely on hue alone. A learning distinction should also be visible through one or more of: label, position, shape, line style, icon/state, value, caption, or interaction state.
