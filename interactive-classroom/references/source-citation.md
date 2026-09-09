# Source, Citation, and Bibliography Contract 

Use stable `course.sources` IDs. A citation is either a source ID or `{sourceId, locator, note}`. Citations may live on knowledge blocks, semantic blocks, formula objects, examples, or evidence sections.

The runtime numbers bibliography entries by source order, renders inline citation chips such as `[2] Chapter 4`, aggregates a per-scene source trail, and exposes a full-course bibliography dialog. The HTML remains offline: bibliographic metadata is embedded text and is not fetched at runtime.

Use `meta.sourcePolicy: grounded` when each core scene must be sourced. Never fabricate page numbers, URLs, DOIs, or exact quotations. If only a general textbook/chapter is known, cite that honestly without an invented locator. User-provided notes/files are primary sources for user-scoped courses.
