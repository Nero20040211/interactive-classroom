# Widget: code

Default to deterministic **code tracing/debugging**, which works offline for any language as authored steps.

Required:
- language label;
- code shown in a readable `<pre><code>` block;
- task: predict output/state, find bug, order steps, or trace variables;
- expected output/state authored explicitly;
- line/step highlighting when useful;
- explanation/debrief.

Do not claim arbitrary code executed unless an actual embedded runtime is present. Native JavaScript execution may be added only deliberately with sandboxing; multi-language runtimes are not assumed.
