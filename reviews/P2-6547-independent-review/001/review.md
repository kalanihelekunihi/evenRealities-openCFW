# Independent review 6547

Disposition: **PASS_SCOPED**; `accepted:false`.

The 264-byte source span 0x415BF6..0x415CFE and packet hashes match. GNU decoding confirms the 56-byte frame, saved registers, output/argument/count setup, and ordinary-byte behavior: with a nonnull output, LF conversion freshly reads the format-global byte and may emit CR before the original byte; with null output it advances/counts without reading the global. The percent parser initializes its pad and long-long state, handles one optional leading zero, calls 41595C for width, and uses its stack output count to locate the specifier. Precision-star consumes one argument word; numeric precision uses a second 41595C call. One or two `l` modifiers update the cursor and long-long flag as described. The dispatch comparisons land at the listed targets for F/f, X, c, d/i, s, u, x, and default.

The packet correctly leaves width-star handling, parser semantics, and all target continuations outside scope. No canonical files or gates changed.
