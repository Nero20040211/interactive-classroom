# Visual Style Sources

This note records public GitHub projects used as **design references only**. The classroom shell remains an original, self-contained implementation and does not import remote CSS, fonts, JavaScript, or assets.

## Reference set

### Edward Tufte / `tufte-css`
Adopted ideas:
- warm paper rather than bright dashboard chrome;
- strong editorial hierarchy from typography and whitespace;
- a constrained reading measure instead of full-width prose;
- figures/captions treated as teaching material, not decorative cards.

Not adopted:
- bundled ET Book fonts;
- the very narrow 55% paragraph layout, which is less suitable for Chinese text plus interactive widgets.

### `kevquirk/simple.css`
Adopted ideas:
- one centered readable text measure;
- responsive heading sizes;
- explicit overflow protection for long text;
- simple semantic form controls instead of component-heavy UI.

### Pico CSS / `picocss/pico`
Adopted ideas:
- semantic design tokens;
- predictable spacing scale;
- clear focus/interaction states;
- responsive typography and controls;
- system-font-first rendering.

No Pico runtime or stylesheet is included in generated HTML.

### Just the Docs / `just-the-docs/just-the-docs`
Adopted ideas:
- documentation-first hierarchy;
- quiet persistent course navigation plus page-local outline;
- compact list rhythm;
- content hierarchy that stays readable without wrapping every block in a card.

### Primer CSS / `primer/css`
Adopted idea:
- foreground/background semantic token pairs (`fg`/`bg`) instead of assuming one global text color works on every semantic fill.

This directly informs the process-animation palette: every semantic actor role has an explicit background, outline, and label color in both light and dark mode.

## synthesis

The resulting classroom direction is:

**editorial textbook measure + documentation navigation + semantic accessible controls + explicit animation foreground/background pairs**.

The implementation deliberately avoids copying any one template pixel-for-pixel.
