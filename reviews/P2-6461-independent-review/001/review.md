# Independent review 6461

Disposition: **PASS_SCOPED**; `accepted:false`.

The F25C..F2FA source bytes and packet hashes match. GNU Thumb decoding confirms the continuation shares the prior 8-byte R7/LR frame. A fresh literal-backed byte gates the first branch: zero skips to F2F6; nonzero calls F1C8(0), ignores its result, then freshly RMWs a different hardware word to set bits10..13 to 1.

It next freshly reads a full word, computes wrapped `word+9`, and compares that full result unsigned to 128. If below 128 it freshly rereads the word and recomputes `+9`; otherwise it selects 127. That value is inserted into bits0..6 of a separately freshly read destination word. A different fresh word is ORed with 0x100. The same full-word procedure is applied with +15 for a second seven-bit field, then another distinct word is ORed with 0x60000000. It calls F1C8(1), ignores the result, and calls 41D1C0(15) before joining F2F6.

The non-gate path at F2E0 uses the current R0 base to read low6, adds 5, freshly reloads the word, inserts low6 into bits0..5, stores, and calls 41D1C0(15). F2F6 returns zero through POP {R1,PC}, exposing incoming R7 in R1. The separate reads and potential wrap are retained; the thresholds are not computed from low-seven-bit-masked reads.

This is static local-flow evidence only; no hardware/register purpose or atomicity claim. No canonical files or gates changed.
