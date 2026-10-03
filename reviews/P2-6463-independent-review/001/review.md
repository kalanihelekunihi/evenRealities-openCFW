# Independent review 6463

Disposition: **PASS_SCOPED**; `accepted:false`.

The F2FA..F38E packet/source hashes match. GNU Thumb decoding confirms an 8-byte R7/LR frame and a fresh gate read of bits4..5. When the field is not 3, the body freshly reads a captured low-six-bit value and BFI-inserts it into a separately fresh hardware word, then does the same with a low-four-bit captured value into bits10..13 of another hardware word before joining cleanup.

For gate value 3, a fresh flag byte of zero skips the enabled updates. Nonzero calls F1C8(0), ignored, then performs ordered fresh capture/source reads and BFI writes: low2 into bits29..30; low7 into a different word's bits0..6; clears bit8 in another fresh word; writes a further captured low7 value into another word; and writes a fresh low4 into bits10..13. It then calls F1C8(1), ignored. Both gate paths call 41CDE0(0,0), ignore its return, set R0=0, and `POP {R1,PC}` returns incoming R7 in R1. The distinct captured literals and destination words are preserved as separate operations.

This is local static instruction evidence only; hardware field purpose and atomicity are not inferred. No canonical files or gates changed.
