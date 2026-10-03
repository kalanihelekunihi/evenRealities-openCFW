# Independent review 2457

**Result:** PASS_SCOPED.

Candidate: `g2/build/pseudocode-first/20260930T190500Z/analysis/touch-mode-two-original-version-failure-2456/001`. Receipt SHA-256 `051f311afda3cce4343d157599d2f75f9eeb22ddd2376621a04178549ae6c2ef`; all four artifact hashes match. Both body spans match the pinned source image hash `371d8a61b659a33b4cad4a7d892e144aba8263ae59497b4f658afc5b0c430f87`.

The harness replayed in an isolated output directory and passed all 40 cases. The cases cross prior modes 0/1/5/6/7 with version bytes 0/1/3/255 and descriptor flags zero/all-set. Original 6AC0 and 8FD0 execute; only the three port helpers are controlled. The assertions verify the ordered helper arguments and subsequent descriptor/parameter clears, loader arguments, no configuration-register writes on version mismatch, unchanged old mode, translated status 64, and R4–R11/SP.

The observed ordering is consistent with the code: the port setup occurs before the original loader’s version check, while successful mode replacement and later peripheral writes are skipped on the tested mismatch path. The child return values are deliberately ignored, so the port helper controls do not establish real peripheral effects.

**Limits:** This covers only request 2, valid non-equal prior modes, and version-mismatch values. Successful loader copying, other prior modes, and physical port behavior are not demonstrated. Private evidence only; accepted:false, no canonical admission.
