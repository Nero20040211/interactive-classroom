# Three-indicator learner quality gate

A course is not high quality merely because it is complete or interactive. Audit three independent learner outcomes.

## 1. Explanation suitability

For each core objective, the explanation should bridge assumed prerequisites, establish a concrete/visual mental model, define new terminology before relying on it, include at least one worked example, and name a boundary/misconception. The target learner level must be explicit in internal course metadata.

## 2. Principle-revealing animation

When a process animation is used, motion/state changes must reveal the mechanism being taught. Require a declared principle, step focus + change summary, genuine actor state/position/shape/rotation change, and a learner debrief (`principleCheck`) that asks what the process demonstrates. Decorative motion, staged mind maps, and arrow flow do not satisfy this gate.

## 3. Gap-revealing practice

Practice should distinguish kinds of misunderstanding. Under the diagnostic policy, each core objective needs guided, independent and transfer/retrieval practice, at least two distinct `gapTags`, and specific feedback. Useful gap tags include `definition`, `condition`, `representation`, `mechanism`, `calculation`, `boundary`, `transfer`, and Pack-specific misconceptions.

## Cross-cutting visual readability gate

The three learner-quality indicators are only meaningful when the learner can actually read the course. For `learnerQualityPolicy.mode = "three-indicator"`, require `visualQualityPolicy.mode = "reader-first-accessible"` and audit the following alongside the three pedagogical indicators:

- normal learner-facing text contrast target: at least 4.5:1;
- non-text boundaries that carry meaning: at least 3:1 against the surrounding canvas;
- process-animation labels: at least 14 px by contract, with the default runtime using 15 px or larger;
- animation meaning must not depend on color alone: pair hue with shape, label, position, line style, or explicit legend/state text;
- mobile process animations use an internal `scroll-inside` viewport rather than shrinking a wide teaching canvas until labels become unreadable;
- every animation semantic role must define a coordinated fill, stroke, and label foreground rather than inheriting an arbitrary page text color.

Run `python scripts/audit_visual_style.py .` as part of release validation. A visually decorative course that passes the three pedagogical checks but fails this readability gate is not release-ready.
