# Independent review 2577

**Result: PASS_SCOPED.**

The candidate is `g2/build/pseudocode-first/20260930T190500Z/analysis/apollo-boot-power-callback-initializer-original-leaf-profiles-2576/001`. Source, body `[0x41CE52,0x41D0EE)`, literal pool `[0x41D11C,0x41D1C0)`, receipt and artifact hashes match. I ran the replay into a separate output directory; the candidate’s 80 fixtures all pass.

The original initializer and 60-byte clear execute with a MMIO-only write hook. The independent-table oracle checks all 15 words, six initializer flags and neighboring sentinels. It then executes only the selected original `0x42D6C0` three-flag leaf, the four-byte `0x42F670` MOVS/BX LR no-op leaf, or the null path; call result, the B3–B5 bytes, MMIO writes, SP and high registers match. The leaf callback’s state word is zero in these fixtures, while no-op/null preserve the sentinel flag bytes. The candidate does not classify bytes after the four-byte no-op as code.

Other installed callbacks/profiles, nonzero leaf state, physical revision/setup, concurrent mutation and incoming ownership remain unresolved. This is a bounded original composition, not whole-initializer closure. Private evidence only; accepted:false, no canonical admission.
