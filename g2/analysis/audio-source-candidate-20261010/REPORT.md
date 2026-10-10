# Audio source candidate, round 2

## Measured scope

The inventory counted 113 `.c` files directly under `g2/components/audio/*/`. This round composed 3/113 as a deliberately bounded codec subset: request packing/transmission, response/CRC, and encoder setup. These are source reconstructions already present in the repository, not recovered original codec source. The script and exact list are in `g2/components/audio/source_candidate_20261010/`.

Host `cc -std=c11 -O2` compiled 3/3 and `ar` archived 3/3 in `/tmp/g2-audio-source-candidate-host`. `nm -u` showed seven application/platform hooks: `codec_hal_blocking`, `codec_wrapper_delay`, `codec_allocate`, `codec_delay`, `codec_release`, `codec_tick_snapshot`, and `codec_uart_read`. It also showed compiler/runtime symbols for stack checking and zeroing. The archive is not a linked application.

The C-SKY tools exist at `third-party/local-vendor/toolchains/csky-linux-x86_64/bin/`; they are Linux x86-64 binaries. Prior authenticated toolchain receipts in `g2/analysis/nationalchip-dsp-c-compiler-successor-20261009T195245Z/` identify C-SKY Tools V3.10.15 Minilibc abiv2 B20190929 and GCC 6.3.0. That establishes compiler availability, not that stock GX8002 codec was built with this configuration. The Docker execution host was started for an actual `-mcpu=ck804 -O2` compile attempt; see execution result below.

## Architecture boundary

The selected codec response and request sources were reconstructed for ARM stock addresses. Compiling their C expressions under C-SKY can validate syntax and object generation only. `hal_bridge.c` imports an ARM UART implementation with PRIMASK instructions, so it was excluded. No binary object, stock execution array, or unknown-opcode stand-in was added to this source composition.

## Remaining counted work

* **3 selected translation units:** verify the C-SKY compiler outcome (3 compile jobs and 1 archive job); inspect C-SKY undefined symbols and object format after archive success (2 commands).
* **7 application/platform hooks:** identify authentic implementations or reconstruct from original bytes (7 separate provider analyses). The codec UART/allocator/timer paths remain unlinked.
* **110 other audio C files:** classify architecture and dependency compatibility before expanding the archive (110 file reviews, then one build per accepted file). Existing ARM inline assembly and memory maps make mechanical inclusion unsound.
* **Semantic/target proof:** original-byte comparison of each selected function, target ISA identification for codec firmware, hardware ABI validation, and physical test are four separate evidence gates. None is supplied by this archive.

No stock codec firmware build or flashable image follows from this round.
