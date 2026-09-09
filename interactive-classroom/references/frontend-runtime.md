# Frontend Runtime Router

## Purpose

`interactive-classroom` has two delivery profiles. The learning contract is the same; only the renderer/toolchain changes.

### `portable` — zero-build single-file

Use the existing `assets/classroom-shell.html` renderer when the course is straightforward, maximum portability matters, or Node/npm is unavailable. The learner receives one HTML file that opens directly with `file://`.

### `modern-react` — component runtime, generation-time build

Use React + compiled Tailwind CSS + Motion when component/state complexity materially improves maintainability or the learner experience. React/Tailwind/Motion are generation-time dependencies that are bundled into the delivered HTML; they are not remote learner-runtime dependencies.

Pinned scaffold dependencies:

- React `19.2.8` + React DOM `19.2.8`;
- Tailwind CSS `4.3.3` + `@tailwindcss/cli` `4.3.3`;
- Motion `13.1.1`;
- esbuild `0.28.2`.

## Natural-language fast path

Codex should not require the learner to know the words `modern-react`, React, Tailwind, or Motion. A normal request for a **detailed / fine-grained / in-depth teaching course** is enough.

Route directly to `modern-react` when a learning/teaching request contains a strong depth or presentation signal such as:

- Chinese: `详细讲解`, `详细的讲解`, `详细地讲解`, `详细课程`, `精细讲解`, `精讲`, `细致的讲解`, `详尽的讲解`, `深入地讲解`, `深度解析`, `全面讲解`, `系统详细讲解`, `高质量讲解`, `高质量课程`, `交互式详细讲解`, `可视化精讲`;
- English: `detailed course`, `detailed explanation`, `in-depth explanation`, `deep dive course`, `thorough explanation`, `fine-grained explanation`, `comprehensive interactive course`, `rich interactive explanation`.

Examples:

- `我需要一个详细讲解高中物理平抛运动的课程` / `我需要一个详细的讲解物理抛物线运动的课程` → `modern-react`
- `请精细讲解二分查找，并做成交互课程` → `modern-react`
- `I want an in-depth interactive explanation of recursion` → `modern-react`
- `我想学习深度学习` → **not** a depth trigger by itself; continue with complexity routing because “深度学习” is the topic name.

Explicit portable constraints take precedence: `不要/别用 React`, `不使用任何框架`, `原生 HTML/CSS/JS`, `vanilla JS`, `framework-free`, `portable`, `zero-build`, `single HTML`, or equivalent wording → `portable`. A bare subject word such as English `motion` is not treated as the Motion library; the modern-stack fast path requires explicit technology intent such as `Motion library`, `Motion runtime`, `Framer Motion`, or “使用 Motion 库”.

`scripts/select_runtime.py` implements this natural-language fast path for deterministic testing. It returns `modern-react`, `portable`, or `auto`; `auto` means continue with the complexity rules below.

## Complexity routing

After the natural-language fast path, prefer `modern-react` when two or more of these are true, or one is unusually strong:

- three or more independently stateful widgets/scenes share reusable UI behavior;
- synchronized state is shared across multiple views/representations;
- rich enter/exit/layout transitions would be fragile in imperative DOM code;
- a custom visualization needs reusable components, SVG/WebGL integration, or complex gestures;
- the renderer would otherwise add a large imperative branch to `classroom-shell.html`;
- the user explicitly asks for React, Tailwind, Motion, or a component architecture.

Prefer `portable` when the course is mostly reading plus a small number of deterministic widgets, direct `file://` simplicity dominates, or the optional build toolchain is unavailable.

Never choose React merely because it is available. Framework choice remains an implementation decision; the depth trigger is a learner-facing preference for the richer implementation path, not evidence that React itself improves learning.

## Generation/runtime boundary

For `modern-react`:

1. Copy `assets/modern-runtime/` to a temporary course workspace.
2. Keep the canonical Stage/Scene course model independent of React.
3. Generate only components/widget adapters actually needed by the course.
4. Use built-in Modern widgets from `src/runtime-capabilities.json` when available. Course-specific widget types must be added to both `src/widget-manifest.json` and the explicit `generatedWidgetRegistry` in `src/widget-registry.jsx`; the build fails if a custom type is missing from either surface.
5. Build at generation time; local Node/npm use is allowed when available. Keep exact direct dependency pins. The checked-in lock root records those direct pins; when the target Codex/npm environment resolves transitive packages, preserve the resulting complete lockfile in the temporary build workspace for reproducibility.
6. Inline compiled Tailwind CSS, bundled React/Motion JavaScript, and course JSON into final HTML.
7. Deliver built HTML, not `node_modules`, source maps, package caches, or a dev server.
8. If the toolchain is unavailable, fall back to `portable` unless the user explicitly requires React.

Network access during dependency installation is a generation-environment concern, never a learner-runtime dependency.

## Animation and widget boundaries

The shared `process-animation` contract lives in `references/process-animation.md`. `animation-contract.js` normalizes timeline defaults and state interpolation; `model-contract.js` contains deterministic model samplers such as horizontal and oblique projectile motion; `animation-widgets.jsx` adapts those contracts into the Modern `ProcessAnimationWidget`, `MotionLabWidget`, `SimulationWidget` and `EquationWidget`. A discipline adapter supplies concrete primitives and model parameters, but it does not redefine autoplay, pause, replay or reduced-motion behavior.

The default process timeline plays once for the mounted scene. Reduced motion leaves direct, inspectable states and controls but disables automatic progression and interpolation. Every used native teaching widget must be present in both `runtime-capabilities.json` and the explicit registry/manifest checks. `GenericLab` is not a native implementation and must not be used as a delivery mapping; an unavailable capability is an explicit build/routing fallback or a build failure.

The Modern page follows the B learning-workbench layout: `ic-topbar`, `ic-scene-rail`, `ic-reading-column`, `ic-outline-rail` and `ic-footer`. Its CSS is imported only through `build.mjs`'s `/*IC_CSS*/` replacement; `main.jsx` must not import the stylesheet again. This keeps the final HTML's Tailwind/style payload single-injected while retaining the reader-first, narrow-screen and scroll-state contracts.

## React architecture rules

- Use `React.StrictMode` in source/development scaffolds.
- Components and Hooks remain pure; side effects belong outside render.
- Keep state at the narrowest useful boundary; one lab control must not rerender the whole reading document.
- Separate CourseModel data from renderer state; never mutate authored course JSON in-place.
- Use stable scene/widget IDs as keys; avoid array indexes for reorderable instructional content.
- Keep substantial widget families behind an explicit registry so unused families can be omitted.
- Put learner-safe error boundaries around complex widget regions so explanation text survives widget failure.
- Preserve the mature reader shell contract: scene search, session bookmarks, bibliography/source trails, current-page knowledge outline, explicit learning-feedback export, and an offline/privacy note.
- Sanitize authored MathML before any `dangerouslySetInnerHTML` use; ordinary lesson content must remain React-escaped.
- Preserve the scroll-state contract: local interaction cannot jump the reader.

## Tailwind rules

Tailwind is a build-time CSS generator with zero browser runtime.

- Do not construct utility classes dynamically such as `bg-${color}-600`; map variants to complete static class strings.
- Keep reader-first hierarchy; utility classes must not turn every paragraph into a card.
- Prefer semantic wrappers for repeated instructional patterns instead of copying very long class strings everywhere.
- Preserve MathML, print/readability, focus, and responsive behavior.
- Do not use the Play CDN in learner artifacts.

## Motion rules

Motion is optional even inside `modern-react`.

- Use `MotionConfig reducedMotion="user"` and CSS `prefers-reduced-motion` fallbacks.
- Prefer `m` + `LazyMotion`/`domAnimation` instead of importing the full Motion component surface by default.
- Layout/enter/exit motion may clarify hierarchy or state, but never counts as principle-revealing pedagogical animation.
- Mechanism animation still follows `animation-content-fit.md`; Motion is only an implementation engine.
- Avoid continuous ambient motion behind long-form reading.
- Avoid layout animation where it could violate scroll stability.
- Learner-inspected animation remains interruptible and directly state-addressable.

## Offline and security rules

The built learner artifact must contain no remote scripts/styles, CDN imports, `fetch`, XHR, WebSocket, EventSource, `sendBeacon`, remote CSS `url()`/`@import`, remote dynamic imports, remote DOM `src`/`href` assignment, analytics, model endpoints, unpinned `latest` imports, secrets, npm tokens, or source maps with local paths by default.

A network/model connection remains a separate explicit user request and must not silently appear because React was selected.

## Build/output contract

`assets/modern-runtime/build.mjs` compiles JSX with esbuild to an IIFE, compiles Tailwind CSS, then inlines both plus `course.generated.json` into a single HTML file.

The built HTML exposes:

- `interactive-classroom-schema=stage-scene` for the course/schema contract;
- `interactive-classroom-runtime=modern-react`;
- `data-runtime-profile="modern-react"`;
- local renderer identity metadata;
- inline `#course-data` JSON so validators can inspect the course independently of minified JavaScript.

## Release gate

Before shipping a modern-runtime course:

- run the normal course semantic/quality validators;
- run `python scripts/validate_frontend_runtime.py .` on the Skill/scaffold;
- run the actual npm build and browser smoke in the target Codex environment when available;
- verify no remote runtime request/dependency;
- verify keyboard/focus, reduced motion, 320/390 px layout, scroll stability, and no learner-facing crash state.
