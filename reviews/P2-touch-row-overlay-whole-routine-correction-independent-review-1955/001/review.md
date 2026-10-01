# Correction audit 1955 — whole row-overlay routine

**Disposition: withdraw the left-clipping finding in review 1937.** Candidate `touch-row-overlay-whole-routine-1928/001`; receipt SHA-256 `90d577ec596e00671c0722cc5641543262f98800cf8b19194acb73e50a3b467d`.

Withdraw the erroneous left-clipping finding in review 1937. At 0x87B8, BHI branches to 0x873C when windowStart>overlayStart. That path computes the amount from overlayEnd−windowStart and bypasses the later 0x87C6–0x87D4 right-start clipping block. The whole-routine candidate’s left-start statement is consistent with that decoded branch.

The prior 1926 fixture did not distinguish over-boundary writes because both the expected output tail and synthetic source tail were zero. The independently replayed 1946/003 sentinel candidate fixes this: nonzero source backing (0x5A) and destination sentinel (0xCC) make copy extent observable, and all 36 original-instruction traces match the model including extra writes beyond the logical window.

Receipt/source/body/disassembly and all five predecessor pins from review 1937 remain valid. No candidate was edited.

This correction addresses the specific branch/clipping finding; it does not convert the whole-body candidate into a replay-backed semantic review. Its other whole-routine claims and generalization limits remain as stated in the candidate. Canonical admission remains false.
