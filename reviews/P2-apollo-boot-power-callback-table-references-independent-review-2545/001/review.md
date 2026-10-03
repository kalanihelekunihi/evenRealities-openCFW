# Independent review 2545

**Result: PASS_SCOPED.**

The exact candidate `g2/build/pseudocode-first/20260930T190500Z/analysis/apollo-boot-power-callback-table-references-2544/001` binds to the pinned flash image and inventory; the receipt and all artifact hashes match. The isolated scan reproduces one halfword-aligned literal occurrence of `0x20026E38` at `0x41D11C` and 15 syntactic PC-relative LDR candidates. For each, the recorded instruction bytes decode as a PC-relative LDR whose aligned `PC+4` plus displacement reaches that literal; the surrounding 64-byte context hashes match the source.

This is a candidate scan only. Halfword alignment means occurrences can overlap data or instruction interiors. None of the candidate load sites is thereby proven to own an entry or perform a reachable table installation. The scan does not cover computed pointers, MOVW/MOVT sequences, copied RAM images, or indirect references; it cannot establish absence of other uses. The `0x41CE5A` candidate is at the initializer entry’s table-pointer load, but that adjacency alone is not caller/initializer ownership proof. Private navigation evidence only, accepted:false; no canonical admission.
