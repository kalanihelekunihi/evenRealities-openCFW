# Image-B platform read/write dispatch

Pinned loaded-image SHA256 `d23fb40126b434e3c47a605997d25210a3cb80302bad7d6c302aaf790627a941`.

Native `0x10003edc` indexes ten addresses at `0x10012a64`: selectors 0..9 map in order to `0x10003f02`, `0x10003f28`, `0x10003f34`, `0x10003f40`, `0x10003f50`, `0x10003f60`, `0x10003f74`, `0x10003f80`, `0x10003eec`, `0x10003ef8`. `backup_platform_read.c` expresses each branch, including eight halfword conversions, bit masks, split packed fields, A001 MMIO reads, and BSS shadow at native `0x20017398`. Invalid selectors return `-1` as native `0x10003fae` does.

Native `0x1001574c` indexes ten addresses at `0x10012a3c`. Selector 6 intentionally enters the invalid path `0x10015826`; selectors 0..5 and 7..9 perform the corresponding register writes. `backup_platform_write.c` preserves write order and masks. In selector 7, native `mvc` transfers comparison flag C to a register; pinned C-SKY QEMU translator `target/csky/translate_v2.c` implements `tcg_gen_mov_tl(cpu_R[rz], cpu_c)`, so source stores Boolean input byte 1 and byte 0 to hardware offsets +0x44 and +0x40. Selector 9 rereads the input word after MMIO write before updating its BSS shadow, as the native sequence does.

The shadow's native address lies inside CRT clear interval `0x20017090..0x2002d79c`; `backup_initialized_runtime_data.c` now gives it a zero-initialized source definition. A host memory-array fixture with test-only MMIO base substitution passed eight read/write selector, mask, field-packing, shadow and invalid-input cases under ASan/UBSan. This verifies C branch effects only, not original instruction execution or physical registers.

Coherent target receipt `build-platform-io-fixture-round/receipt.json`: 158 units/link PASS, linked SHA256 `2373945c91b25a8151781fa8ee71e965c5de416515b4a94abb5884919aee0344`; eight genuine FP/data/ambient/linker imports remain. Defined-symbol native address crosswalk is 231/288, 57 outside. This address measure does not establish whole-body or loaded-image equivalence.
