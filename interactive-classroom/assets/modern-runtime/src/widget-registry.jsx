import { builtinWidgetRegistry } from "./builtin-widgets.jsx";

// Codex may extend this registry with course-specific components. Built-in
// components cover the core cross-disciplinary regression surface; generated
// components must still be explicit so unused code can be tree-shaken.
export const generatedWidgetRegistry = Object.freeze({});
export const widgetRegistry = Object.freeze({
 ...builtinWidgetRegistry,
 ...generatedWidgetRegistry,
});
