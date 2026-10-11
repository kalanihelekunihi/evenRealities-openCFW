# CASE task-context event clear candidate

The C candidate for `xEventGroupClearBits` at original CASE address `0x0800c44c` is compiled with the existing source-owned critical-section helpers. The authenticated original body spans 42 bytes.

`verify.py` compares the original and freshly compiled source over 72 returning event-bit, interrupt-mask, and critical-nesting states. Four invalid inputs exercise only the bounded nonreturning prefix; no later assertion behavior is claimed. The verifier records hashes and the compiler command in `results.json`.

This bounded body is **COMPLETE** for the tested contract. Its event-group lifecycle, timer callback scheduling, whole CASE image link and physical concurrency behavior remain open. At this round's build, the CASE archive contained 23 source objects with 14 unresolved global names; the subsequent event-set export reduced that count to 13. Those names are provider contracts for review, not a count of missing function implementations.
