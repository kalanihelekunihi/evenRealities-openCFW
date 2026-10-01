# Independent review 1953 — sentinel left-clipping traces

**Result: PASS_SCOPED.** Candidate `touch-row-overlay-left-clipping-sentinel-1946/003`; receipt SHA-256 `2fb6b4ec26003ae9c5a6a0b04c598d6ebe14555df55e0e45dc005f064b8b9291`.

Candidate file hashes and source pin match. Isolated regeneration passes all 36 fixtures and exactly matches the stored replay output. Original CRC, 4860 provider and AA2C copy code execute without interception.

The sentinel backing and destination make copy extent observable: backing begins with 0x5A outside the payload and destination is initialized to 0xCC. For a left-starting overlay intersecting logical [64,128), the trace copies from source delta 64−(offset mod 64) into destination offset zero for overlay_end−64 bytes, including distinguishable writes beyond window end where that amount exceeds the window. Other boundary placements are checked against the piecewise interval model. Full 256-byte output, zero return and SP are asserted.

CRC construction zeroes the checksum word then computes over bytes [1,125); the synthetic source backing is deliberately 512 bytes so the decoded overrun is mapped and visible. This demonstrates instruction behavior for these inputs, not a valid physical row extent.

Trace-only fixed geometry; no claim of valid out-of-row physical layout, general algorithmic coverage, mirrors, concurrency, or canonical admission.
