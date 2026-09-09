# Teacher Action Protocol 

The Action Bus is the offline analogue of an agent driving an interactive widget. It keeps narration synchronized with visible UI changes.

## Action shape

```js
{
 id: "A1",
 actorId: "teacher",
 type: "HIGHLIGHT_ELEMENT",
 target: "node:mitosis",
 payload: {},
 narration: "先看这个阶段。"
}
```

Actions are ordered within a scene. The learner may advance manually. Do not require timed autoplay.

## Core action types

### HIGHLIGHT_ELEMENT

`target` identifies a declared widget element. The widget must visibly emphasize it and keep text/keyboard access.

### CLEAR_HIGHLIGHT

Removes action-driven emphasis.

### SELECT_ELEMENT

Selects a diagram/3D/data element and shows its detail panel.

### SET_WIDGET_STATE

`payload.patch` contains an allowlisted deterministic state patch, such as simulation parameter values or game round state. Clamp numeric values.

### REVEAL_STEP

Reveals an equation/procedure/code/diagram step by ID or index.

### SHOW_HINT

Displays a learner-visible hint. Hints must not masquerade as live model generation.

### RESET_WIDGET

Restores the scene widget to its initial runtime state.

### FOCUS_REGION

Moves selection/spotlight to a defined region without trapping keyboard focus.

## Contract rule

If an action type is declared for a widget, that widget must implement it. Never emit narration like “I highlighted…” if the UI did not change.

## Runtime UI

When `scene.actions` exists, show a compact “教师引导” control with:

- current step count;
- next action;
- replay/reset guidance;
- current narration text.

The action timeline is deterministic and local.
