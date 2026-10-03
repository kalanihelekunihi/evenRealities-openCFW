# Independent review 2795 — handler table private audit

**Result: PASS_SCOPED.** The isolated verifier passed against the pinned flash and decoded RAM artifacts, and all candidate artifact hashes match. It found 27 initialized table targets at `0x20000158`: 24 contiguous mapped handler bodies plus three original `BX LR` leaves. I independently checked the interval coverage, each body’s bytes and instruction count, and the gap calculations: 7,992 mapped bytes, 2,817 instructions, and 11 gaps totaling 634 bytes. The gap bytes remain unclassified by this audit.

This is private table-entry navigation and evidence accounting. It does not establish whole-firmware completeness, complete handler semantics, incoming-edge closure, or ownership of the gaps. The audit remains `accepted:false`; it is not canonical admission or a freeze determination.
