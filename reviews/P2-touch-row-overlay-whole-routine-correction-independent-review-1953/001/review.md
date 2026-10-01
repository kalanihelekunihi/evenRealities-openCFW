# Correction audit 1953 — whole row-overlay routine

**Disposition: withdraw the left-clipping finding in review 1937.** Candidate `touch-row-overlay-whole-routine-1928/001`; receipt SHA-256 `90d577ec596e00671c0722cc5641543262f98800cf8b19194acb73e50a3b467d`.

Correction to review 1937: the earlier left-clipping finding was based on overlooking the conditional branch at 0x87B8. When windowStart > overlayStart, BHI branches directly to 0x873C, bypassing the later 0x87C6–0x87D4 right-edge clamp. The candidate’s pseudocode for this left-start path is consistent with the decoded branch structure; withdraw the claim that this path clamps at windowEnd.

The related fixture limitation remains: in the left-clipping trace offset=60,length=128, destination bytes beyond the logical window are initially zero and source backing beyond its declared row is zero, so full-buffer equality does not distinguish copying extra zeros from leaving them untouched. This is a limitation of that trace assertion, not contrary evidence against the decoded no-clamp path.

Body/source hashes, 183-instruction decode, exact disassembly, and all five parent pins checked in review 1937 remain valid. Candidate files are unchanged.

This append-only note corrects the specific false positive in review 1937; it does not independently validate all whole-routine formulas. The candidate has no replay harness. The left-clipping trace does not prove the write extent where written and unwritten tail bytes match. No canonical admission.

This preliminary correction is superseded by correction audit 1955, which incorporates the independent sentinel fixture result.
