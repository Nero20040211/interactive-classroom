# Process Animation Contract 

Animation is reserved for teaching change over time, transformation, mechanism, physical operation, algorithm state transition, or experimental accumulation.

A mind map that reveals nodes one by one is not a process animation. A dashed moving arrow with otherwise fixed objects is not enough. Those remain valid staged `diagram` techniques and are learner-labeled `分步图解`.

## `process-animation`

Declare stable actors and at least three states. Each step has a short caption, an explicit **观察重点**, and a **本步变化** summary. Actor state may change position, rotation, scale, dimensions, face/state, or opacity. Prefer concrete process actors (`die`, `coin`, domain objects) over generic boxes when that makes the mechanism easier to see. The runtime supplies previous/next/play/pause/replay and respects reduced motion.

Visual clarity is part of correctness: declare safe margins and minimum gaps; prevent unintended visible overlap; declare intentional containment when an actor enters a region; render tracks/regions behind moving actors; and put long explanations in the caption rail instead of over the SVG.

Under `meta.animationPolicy.mode="process-first"`, strict validation requires real geometric/state transitions. Caption-only or reveal-only diagrams do not qualify.

Good uses include moving projectiles, DNA opening and synthesis, geometric construction, independent random devices combining outcomes, experimental accumulation, and algorithm state changes.

## label and color readability

A mechanically correct animation can still fail instructionally if learners cannot read its labels.

- Use semantic role palettes with explicit foreground/background pairs.
- Normal actor labels should meet a 4.5:1 contrast target against their actor fill; important actor outlines should meet a 3:1 target against the animation canvas.
- Default in-shape labels should be about 15–18 CSS px at rendered scale. On narrow screens, preserve that scale with an internally scrollable animation canvas rather than shrinking the entire SVG.
- Avoid placing paragraph-length prose inside the SVG. Keep long explanations in the caption/focus rail below the moving objects.
- Do not use color as the only state cue. A color change should be paired with movement, label, symbol, shape, opacity/state, or explicit caption.
- Run `scripts/audit_visual_style.py` and browser smoke checks in both light/dark-capable CSS and mobile width before release.
