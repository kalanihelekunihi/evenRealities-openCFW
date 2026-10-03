# Independent review 2471

**Result:** PASS_SCOPED.

Candidate: `g2/build/pseudocode-first/20260930T190500Z/analysis/touch-mode-two-port-list-root-mutation-2470/001`. Receipt SHA-256 `e23dbcd9bcca9799e35d7479d1fa3024443d5760694bf89ab058475d2547d512`; all four declared artifact hashes match and all five spans match the pinned source image.

The isolated replay passed all 160 fixtures. Original 6AC0, 6078, 60EA, 6044, and 8FD0 execute; only 5FC6 is controlled. The first primary child replaces ctx.word0 with a root whose primary count is zero and secondary count is one. The primary and secondary list loops reload their respective counts and stop after one entry; the secondary child then clears its count. The paired wrapper still performs its two calls from the replacement root. The replay asserts the four pin-call tuples, two direction writes, unchanged mode/loader outcome, status, and R4–R11/SP.

**Limits:** The old and replacement roots share a table pointer, so this does not establish differing-table behavior. It does not test increasing counts, replacement cursor changes, physical port effects, or concurrent mutation. The note that the dispatcher retains its initial root is bounded to this fixture’s loader pointer arrangement. Factory/MMIO are modeled; accepted:false, no canonical admission.
