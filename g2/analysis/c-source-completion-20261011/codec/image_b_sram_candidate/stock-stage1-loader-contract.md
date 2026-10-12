# Stock image-B stage-1 loader contract

Input `binh_b_stage1.bin` SHA-256 `a80924ccf78205ef1761c4f568d4ce31f909635bf3ad7eecfaed250ad801626c` and `binh_b_stage2.bin` SHA-256 `d23fb40126b434e3c47a605997d25210a3cb80302bad7d6c302aaf790627a941` are in `g2/build/pseudocode-first/20260930T190500Z/reviews/codec-canonical-images-003/images/`. The 24-byte BINH header is file-only; stage-1 runtime addresses equal file offsets plus `0x0fffffe8`. Disassembly uses `--adjust-vma=0x0fffffe8`.

Stage-1 entry `0x10000100` sets SP `0x20002ffc`, calls `0x10000df0`, then transfers to `0x10003100`. `0x10000df0` calls setup functions, checks `*(uint32_t *)0x20001720 == 2`, and in that branch calls `0x10000d4c`. The latter is the stock image-B loader:

* `0x10000d50..0x10000d5c`: read package offset at `0x20001724`, add the 12 KiB stage-1 extent.
* `0x10000d5e..0x10000d6a`: test retained marker `0xaabbccdd` at `0x20033ffc`; the ordinary branch reads four bytes from the package via `0x10000fdc` into a local word.
* `0x10000d70..0x10000d84`: form the destination `0x10003000`, source offset `package + 0x3000 + *(local word) + 4`, and byte count `0x2001708c + 0x100167d0 - 0x10003000 - 0x200167d0 = 0x1408c` (82,060).
* `0x10000d84` calls the native flash reader `0x10000fdc` with that source, destination, and count. The reader's `0x10000fdc..0x10001098` prologue saves r0/r1/r2 as flash address, destination, and remaining count, then configures the memory-mapped flash reader and stores bytes to the destination. `0x10000d88..0x10000d94` writes boot state and jumps to stage-2 entry `0x10003100`.

The stage-2 binary is exactly `0x1408c` bytes. Its final 300 bytes occupy load addresses `0x10016f60..0x1001708c`. The package BINH header also declares `0x1408c` at offset `0x0c`. This stock instruction sequence establishes one contiguous stage-2 load into IRAM; a stage-2 CRT copy is not required to account for the flash payload. The typed C records place those final 300 bytes at runtime DRAM addresses `0x20016f60..0x2001708c`, following the pinned GX8002 SDK linker alias/dummy-section model. Whether this exact stock device aliases those IRAM and DRAM ranges is still a hardware/SoC mapping qualification gate. The marker-selected alternative branch at `0x10000d9a` loads a different payload and is not covered by this stage-2 normal-branch claim.

Reproduce the native slice with `/tool/bin/csky-abiv2-elf-objdump -D -b binary -m csky --no-show-raw-insn --adjust-vma=0x0fffffe8 --start-address=0x10000d4c --stop-address=0x10000dd0 /stock/binh_b_stage1.bin`, using the pinned C-SKY toolchain mount in `verify_audio_buffers.py`.
