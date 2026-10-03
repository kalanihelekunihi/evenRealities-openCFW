# Independent review 2503

**Result:** PASS_SCOPED.

Candidate: `g2/build/pseudocode-first/20260930T190500Z/analysis/apollo-shared-itcm-delay-copy-2502/001`. Receipt SHA-256 `b0871c547a498c89313d843534ce6eb082ce439efcc5583254c80d33c01a6198`; all declared artifact hashes match. The pinned inventory digest matches the current inventory. Both source artifacts are 24-byte decoded spans with identical digest `0676154418085b0630f2a20cc50fbbe3967dd2d9b7794fe1aad3f6af14f2fb83`; the inventory maps each image span `[0,24)` to loaded `[0x40,0x58)`. The disassembly agrees with the bytes: delay loop at 0x40, returns at 0x44/0x46, postincrement word-copy loop at 0x48, returns at 0x54/0x56.

The isolated replay passes all 54 fixtures. It covers both decoded images, positive delay counts, bounded zero-count prefixes, word-copy counts, forward overlap by four bytes, same pointer, backward overlap, separate buffers, and direct duplicate-return entries. The tested overlapping copy behavior follows live load/store order; the forward-overlap case propagates the first word as stated. Whole-RAM, write, pointer, result, and register assertions pass for the bounded cases.

**Limits:** The zero-delay loop decrements modulo 32 bits and does not terminate from zero; only three-iteration prefixes are exercised. This does not establish a completed zero-count call. The duplicate BX LR instructions at 0x46 and 0x56 are decoded and exercised, but their entry ownership is unresolved; they are not labeled padding. Physical timing, alignment/fault behavior, and broader incoming-entry ownership remain open. Private evidence only; accepted:false, no canonical admission.
