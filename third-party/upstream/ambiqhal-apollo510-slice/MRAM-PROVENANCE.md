# MRAM provider source/API boundary

## Acquired candidate closure

The pinned HAL source directory now includes these additional exact files from gitlink `5efc0228528a8adce5eae0d226fac85d2551eb3b`:

- `am_hal_mram.c/.h`
- `am_hal_interrupt.c` and Apollo510's actual public header `am_hal_mcu_interrupt.h`
- `am_hal_bootrom_helper.c/.h`
- `am_hal_pwrctrl.c` (needed for the ROM power-domain entry points)

Per-file SHA-256, origin, notices, and release markers are in `FILE-PROVENANCE.tsv`; all hashes are in `SHA256SUMS`. These files carry Ambiq copyright and BSD-3-Clause notices. Note that the pinned `am_hal_pwrctrl.c` file itself contains the distinct marker `release_5p1p0beta-2927d425bf`, even though the HAL MSPI/MRAM files identify `release_sdk5p1p0-366b80e084`. It is a precisely pinned source file, but should not be represented as having the same file-local release marker as the MRAM implementation.

There is no Apollo510 file named `am_hal_interrupt.h` in this revision; the function declarations for global master interrupt helpers live in `am_hal_mcu_interrupt.h`. No extra C sources beyond those listed were required to compile these translation units.

The following all compile as standalone Cortex-M55/Thumb ARM EABI5 objects with Clang and the existing Apollo510/CMSIS headers: `am_hal_mram.c`, `am_hal_interrupt.c`, `am_hal_bootrom_helper.c`, and `am_hal_pwrctrl.c`. The MRAM object still has expected external references to master interrupt save/restore, ROM power enable/disable, and `nv_program_main2`; the separately compiled interrupt and bootrom-helper objects define some of these, while `am_hal_pwrctrl.c` in turn has broader power/spot-manager state dependencies. This is compile evidence, not a complete target link.

## Recoverable provider contract

The public header gives a direct API candidate for the aligned update-record write:

```c
uint32_t am_hal_mram_main_program(uint32_t key, uint32_t *src,
                                  uint32_t *dst, uint32_t num_words);
```

`AM_HAL_MRAM_PROGRAM_KEY` is `0x12344321`. This API rejects destinations that are not 16-byte aligned and word counts that are not a multiple of four. Therefore a 16-byte record write has a natural 4-word call shape. The worker copies the exact public source and does not assert that the raw function at `0x0042e8a4` is byte-identical to this API; raw Ghidra currently names that address `guarded_call_cleanup_42e8a4`, and the raw decompilation is not reviewed source. Parent-side address and call-graph changes should determine which target leaf is the provider before applying a name match.

The pinned implementation performs these source-visible operations:

1. Validate 16-byte destination alignment and four-word count granularity.
2. In the shared word-program path, convert the main-MRAM byte destination to a word offset using `(dst - AM_HAL_MRAM_ADDR) >> 2`.
3. Enter `AM_CRITICAL_BEGIN/END`, whose Apollo510 definitions disable master interrupts and restore the saved prior interrupt state.
4. Call `am_hal_pwrctrl_rom_enable()`, invoke `nv_program_main2(key, AM_HAL_MRAM_PROGRAM, (uint32_t)src, word_offset, count)`, then call `am_hal_pwrctrl_rom_disable()`.
5. Map a zero ROM status to HAL success; otherwise OR the result with the MRAM module error base.

`am_hal_bootrom_helper.c` defines the `nv_program_main2` helper-table entry as Thumb address `0x0200ff20 + 1`. Its wrapper calls that ROM function and then performs the controller cleanup writes `0x40014008 = 0xC3`, `0x40014024 = 0`, and `0x40014008 = 0`. Those addresses are the MRAM status/control cleanup in the public helper source; they must not be confused with the board/guard logic around address `0x40000008` found in separate target context. The helper-table code supplies the ROM service address and ABI, not the ROM implementation. The contents and behavior of the `0x0200ff20` ROM service remain external.

The public MRAM implementation itself does not install a cache guard or callback. Its external runtime edges are the saved interrupt-state helpers, ROM power gating and power-state support, and the fixed-address ROM service table. Any target-side MSPI guard/bypass or cache-maintenance callback is separate wrapper/platform behavior and remains to be matched from the firmware call graph. Do not infer ROM internals, callback semantics, or a write to a particular update-record address from this generic API alone.

## Evidence boundaries

- Public source: `ambiqhal/mcu/apollo510/hal/mcu/am_hal_mram.c`, `.h`, `am_hal_bootrom_helper.c/.h`, `am_hal_interrupt.c`, and `am_hal_pwrctrl.c`.
- Raw target extract inspected: `g2/research/corpus/apollo-bootloader/ghidra/open-2026-09-29/decomp/0042e8a4.c`; it shows an indirect cleanup callback and state writes, but has placeholder globals and does not itself prove the public MRAM call sequence.
- Public-source API contract and ROM function table are strong implementation evidence, not exact target source matching. No IAR code generation, full link, ROM execution, or hardware test was attempted.
