# Independent review 2581

**Result: PASS_SCOPED.**

Candidate `g2/build/pseudocode-first/20260930T190500Z/analysis/apollo-boot-installed-callback-frontier-2580/001` binds to the pinned flash image and initializer map. The receipt and all declared artifacts hash correctly. The referenced initializer map hash and bootloader symbol-table hash are recorded in the generated frontier. I reran the verifier into an isolated directory; its frontier output matches the candidate exactly: 29 unique targets, 31 stores/assignments, four slot-zero initialization targets and 11 exact historical bounded ranges.

The scan requires each `STR R0,[R5,slot]` to be immediately preceded by a PC-relative `LDR R0,[PC,...]` carrying a literal, resolves the original pointer, and retains each assignment/profile. It binds exact entry addresses to bounded symbol rows and rehashes the candidate body bytes. The verification establishes a reproducible navigation frontier from those literal/store patterns.

Syntactic candidates and historical symbol ranges do not prove ownership, reachability, complete function boundaries, body behavior, callback installation at runtime, or absence of other pointer construction/indirect use. The report’s `initialization_targets` count is not semantic admission. This is prioritization evidence only; accepted:false and no canonical admission.
