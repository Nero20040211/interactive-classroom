# `process-animation`

Use only when the learning objective depends on observing a **real process change across time**. A reveal-only mind map, flow chart, or blinking arrow is a `diagram`, not an animation.

Required: `principle`; at least one stable actor; at least three steps; every step has `title`, `caption`, `focus`, `changeSummary`, and `states`; at least two real position/rotation/shape changes across adjacent steps.

Supported primitives include `circle`, `rect`, `line`, `text`, plus concrete teaching primitives `die`, `coin`, `track`, and `zone`. Prefer concrete primitives when they clarify the mechanism.

## Readability / no-overlap contract

Every process animation should declare `layoutPolicy` with `safeMargin`, `minGap`, and `preventOverlap:true`. Moving actors must remain inside the safe canvas. Non-container actors must not overlap at any visible step. A `zone` may intentionally contain actors only when it declares `contains:[...]`. Long explanatory text belongs in the caption/focus rail below the SVG rather than over a motion path.

The validator checks static step layouts; browser smoke tests must still inspect intermediate transitions at desktop and mobile widths.

Do not imitate a process by merely revealing static boxes. Use `diagram` for that.


## principle check

Under `learnerQualityPolicy.mode="three-indicator"`, include `widgetConfig.principleCheck` with a learner-facing prompt that asks the learner to explain what the changing objects/states demonstrate. This is distinct from the step caption.


## content-fit extension

Read `../animation-content-fit.md` and `../discipline-animation-profiles.md`. Content-fit animations require `animationSemantics`, domain-native actors when available, per-step `semanticAction` / `whyItMatters`, key-step emphasis, and `principleCheck`.
