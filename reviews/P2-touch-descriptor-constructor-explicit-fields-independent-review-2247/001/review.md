# Independent review 2247

**Result:** PASS_SCOPED.

This append-only correction pins the same source, constructor body `[0x5548,0x569E)`, and literal `[0x56A0,0x56A4)` as the reviewed candidate. All file hashes match. The newly explicit first-word expression matches the decoded operations: low configuration nibble at bits 0–3, low nibble of configuration byte 93 at bits 4–7, low nibble of byte 94 at bits 8–11, six masked bits from parameter halfword 12 at bits 16–21, and configuration byte 95 at bits 24–31. The expression’s `& 255` after byte93 shifted by four is equivalent to retaining those low four source bits.

An isolated replay regenerated all 144 fixtures. It retains the corrected independent parameter byte 32/33 values and assertions for ordered destination writes, full output, child arguments/status, and preserved registers. The prose correction closes review 2241’s specific pseudocode gap.

**Limits:** Child `0x51BC` remains controlled, and fixture patterns, indices, kinds, and child statuses remain bounded as recorded in review 2241. No physical field meaning or canonical admission is established.
