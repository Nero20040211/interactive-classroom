# Front-end craft 

This note describes the **portable renderer** craft baseline. The same visual principles also apply to the optional locally bundled `modern-react` renderer; see `frontend-runtime.md`.

## Detail.design

Use small considered decisions: interruptible motion, anchored navigation, clear focus states, platform-appropriate copy, visible state changes, and no layout shift merely to signal active state. Micro-interactions should remove friction rather than compete with the lesson.

## Launch UI

Borrow section rhythm, faint structural rails, quiet gradients/glows, balanced containers, and clear hierarchy between hero/header, content, and embedded interactive surfaces. Reinterpret these as a textbook/course shell rather than a landing page.

## Magic UI App Template

Borrow restrained ambient gradients, short staggered entry motion, rounded high-quality surfaces, and visual depth. Continuous floating/marketing motion is inappropriate for reading and is disabled; `prefers-reduced-motion` removes entry transitions.

## Guardrails

- portable renderer: no CDN/framework dependency; modern-react: React/Tailwind/Motion may be bundled locally at generation time, but no learner-runtime CDN/external JS/CSS;
- reading width and hierarchy remain primary;
- animation text contrast remains >= 4.5:1;
- mobile process animation preserves readable labels via internal horizontal scrolling;
- active states must not change layout width;
- process playback is interruptible and every step is directly reachable;
- decoration never counts as pedagogical animation.
