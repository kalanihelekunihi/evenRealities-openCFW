# Independent review 2875

Status: **REVISE_PROSE** (`accepted: false`).

The source hash matches the inventory image, the body `[0x42AC54, 0x42ACA4)` matches its claimed digest, and the candidate artifact hashes verify. The isolated static replay regenerated 35 instructions with exact byte coverage. I checked the guard order, callback arguments, the `0xC2200000` VFP literal, and the `POP {r1, r2, r3, pc}` epilogue against the original instructions.

One literal address in the prose needs correction. At `0x42AC86`, the `LDR r1, [pc, #0xb4]` resolves using aligned PC `0x42AC88` to pool address `0x42AD3C`, which contains `0x400083E0`. The prose calls this “literal42AD40”; the word at `0x42AD40` is `0x0A04EEFB`, so it is not the poll pointer. State the pool address `0x42AD3C` separately from the loaded argument value `0x400083E0`.

The static candidate’s stack-alias discussion is bounded to its call and epilogue. It does not establish broader callee behavior, polling hardware, startup ownership, or whole-image completeness. No canonical admission is claimed.
