# Independent review 2547

**Result: PASS_SCOPED.**

The candidate `g2/build/pseudocode-first/20260930T190500Z/analysis/apollo-boot-power-callback-initializer-control-map-2546/001` binds to the pinned flash image and inventory. Receipt and all three declared artifacts match their hashes. I ran `verify.py` from an isolated copy; the exact span `[0x41CE52,0x41D0EE)` decodes contiguously to 304 Thumb instructions and the generated map matches the candidate byte-for-byte. Its sole decoded direct call is `0x41560C`; local direct branch destinations are instruction-aligned. PC-relative literal entries use aligned `(PC+4)` addressing and retain the source words, including the table pointer literal resolving to `0x20026E38`.

This is a static control-flow/literal map. The revision-selection and callback-assignment prose is explicitly navigation-level; no dynamic fixture validates those paths or repeated-read freshness. The one direct call is identified, but indirect callback targets, installed callback ownership, incoming callers, hardware setup and physical register behavior remain open. Literal data is not promoted to code, and no whole-firmware coverage or canonical admission is claimed. Private evidence only; accepted:false.
