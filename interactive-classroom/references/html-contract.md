# Offline HTML Contract 

Read this before generating or revising a classroom file.

## Default runtime constraints

The delivered classroom must work when opened directly from disk in a current modern browser.

Forbidden by default:

- `fetch(`
- `XMLHttpRequest`
- `WebSocket`
- `EventSource`
- external `<script src="https://...">`
- external `<link rel="stylesheet" href="https://...">`
- remote fonts required for layout
- OpenAI/Anthropic/Gemini/other LLM API calls
- required server routes
- required **learner-side** npm/pnpm build
- analytics/trackers

Allowed:

- inline `<style>` and `<script>`;
- SVG;
- Canvas;
- Web Animations API with reduced-motion fallback;
- Pointer Events;
- local embedded JSON/JS data;
- browser-native controls;
- deterministic numerical simulation;
- locally bundled React/Motion code and compiled Tailwind CSS when using the stable `modern-react` profile;
- generation-time Node/npm/build tooling when the final delivered artifact remains offline and directly openable.


## Renderer profiles

The default `portable` renderer uses the inline structure below. The optional `modern-react` renderer may be authored with React/Tailwind/Motion, but its generation-time build must inline/bundle the result so the learner receives an offline artifact. Modern output keeps the same course schema and exposes `interactive-classroom-runtime=modern-react` plus inline `#course-data` JSON for validation. Read `frontend-runtime.md`.

## document marker

Full classrooms should include:

```html
<meta name="interactive-classroom-schema" content="3">
```

and a learner-visible offline note such as:

> 离线课堂：本页面不会向外部模型发送你的输入。

## Structure

Prefer:

```html
<!doctype html>
<html lang="zh-CN">
<head>...</head>
<body>
 <main id="app" data-interactive-classroom="">...</main>
 <script>
 const course = {...};
 const state = {...};
 // renderers + local interaction
 </script>
</body>
</html>
```

## Event architecture

- initialize listeners once;
- use event delegation for rerendered regions when useful;
- reset restores initial state and graph layout;
- clean up timers/animation frames if used;
- prevent repeated listeners on scene rerender.

## SVG interaction

For draggable knowledge nodes:

- use Pointer Events;
- clamp node positions to viewBox bounds;
- keep page scrolling available outside the graph;
- add keyboard arrow movement for focused nodes;
- preserve an accessible text relationship summary.

## Accessibility

- semantic buttons/inputs;
- visible labels;
- keyboard access;
- focus rings;
- `aria-live` for concise dynamic correctness/status feedback;
- sufficient contrast;
- no color-only correctness encoding;
- reduced-motion support;
- touch targets about 44 px when practical.

## Responsive behavior

At ~320 px width:

- no page-level horizontal scrolling;
- classroom shell becomes one column;
- role strip wraps;
- navigation is usable;
- charts/SVG resize with `viewBox` or local scroll only if unavoidable.

## State safety

- initialize all state keys;
- numeric inputs use finite checks and clamping;
- do not display `undefined`, `NaN`, or `Infinity`;
- reset is deterministic;
- selected visual items stay selected until changed/dismissed.

## Assessment honesty

Do not claim “AI grading” unless an actual model connection exists.

For free text use:

- normalized exact match only for short factual responses;
- transparent deterministic rules;
- self-rubric/checklist;
- invitation to paste the response back into Codex for model feedback.

## Privacy

Do not collect or transmit learner data. No hidden network calls.


## Local action bus

The shell may execute authored teacher actions locally. Action dispatch must never access the network, eval arbitrary remote code, or silently ignore a declared action.

## Embedded media

`data:` URI media is allowed in strict offline mode. Remote `http(s)` media is not.

## reading-state contract

Follow `scroll-state-contract.md`: local interactions preserve viewport position, scene navigation targets the scene heading, and the page-level TOC uses direct anchors without re-rendering. Follow `visual-inspiration.md` for the documentation/textbook visual hierarchy.

## learner-readable visual contract

For three-indicator courses, internal JSON declares `visualQualityPolicy` with `mode: reader-first-accessible`, text/non-text contrast targets, a minimum animation label size, `avoidColorOnlyEncoding: true`, and `mobileAnimationStrategy: scroll-inside`. The learner HTML does not expose this engineering metadata; it only receives the resulting readable layout.

Wide instructional SVGs may scroll inside their own stage on narrow screens, but the page itself must not horizontally overflow. Do not globally scale a wide process canvas below its readable label size merely to fit a phone viewport. Process actors must use explicit semantic fill/stroke/text triplets, and their text must remain readable in both light and dark color schemes.
