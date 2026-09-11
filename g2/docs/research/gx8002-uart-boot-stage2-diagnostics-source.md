# GX8002 UART boot stage 2 diagnostics window (CD-006)

Scope: package `[0x7204, 0x9204)`, 8,192 retained bytes, a slice of the
authenticated UART boot stage 2 envelope (`gx8002-uart-boot-stage2-boundary.md`
covers the full `[0x2850, 0x958C)` typed-provider boundary; `CD-003`'s
`gx8002-uart-boot-stage2-reset-source.md` covers the first 2,452 bytes of that
same envelope). Runtime `0x100071B4..0x100091B4`. This document narrows that
boundary with named, individually qualified data leaves; it does not change
the typed-provider boundary's own claims, and it does not close the item.

## Layout established by disassembly

Disassembling `[0x7204, 0x9204)` with the C-SKY objdump against an existing
whole-image wrapper ELF (`build/gx8002-board/padmux-get-stock.elf`, VMA 0 ==
package offset) shows a clean split:

| Package range | Bytes | Content |
| --- | ---: | --- |
| `[0x7204, 0x7F22)` | 3,358 | Executable code: a segregated-fit allocator (20-byte size-class index via `mula.32.l`, `bhsz`-loop leading-bit search, free-list link/coalesce) and several small comparator leaves that tail-branch to a shared epilogue at `0x7E98`. Not attributed to any pinned upstream source; not reconstructed by this pass. |
| `[0x7F22, 0x85B4)` | 1,682 | Printf format strings and short label/name strings, interleaved with two small `uint32_t` address tables. Six strings are attributed and admitted below (83 bytes); the remainder is undisturbed. |
| `[0x85B4, ~0x8600)` | ~76 | `"boot> "`, `"<INTERRUPT>"`, and format strings for the command-help printer, continuing the U-Boot-derived command-line cluster documented in `peripheral-oss-library-provenance-audit.md` (package offsets `0x8364`-`0x8650` in that audit's numbering, which uses "stage 1" for the whole `[0x30,0x958C)` UART-boot container). |
| `[~0x8600, 0x9204)` | ~3,076 | A command-table structure (name/usage/handler entries for `help`, `eraseall`, `erase`, `flash`, `do_serialdown`, `reboot`, `wdt`, `usbslave`, `ping`, `write`, `read`, `init`) referencing the same U-Boot-derived cluster, plus flash-device probe/OTP messages and the six SPI-NOR device-name strings already admitted elsewhere for a different occurrence (`gx8002-flash-device-names-verification.json`, package offset `0x153e0` in `image_a_xip_text`; this window's copy is at `0x8134`-`0x8160` and is a distinct, unclaimed occurrence). |

## Six diagnostic strings admitted this pass

`runtime_gx8002_uart_boot_stage2_diagnostics.c` /
`verify_gx8002_uart_boot_stage2_diagnostics.py` reconstruct six literal printf
format strings as `generated_source_data`, each its own
`__attribute__((aligned(1)))` `const char[]` compiled with the codec's usual
`-O2 -mcpu=ck804ef -mhard-float -ffreestanding ...` flags. Each is verified
two ways: the compiled section's bytes equal the stock bytes at its package
offset (the actual completion requirement), and they equal the literal text
extracted by regex from the pinned NationalChip `lvp_kws` SDK source file
that contains the matching `printf(...)` call (commit
`8bf9ee5cb6eeb226011e61c15fa4981b83b93bd5`, MIT, `NATIONALCHIP-UART-BOOT-STAGE2-DIAGNOSTICS-NOTICE.txt`),
for provenance.

| Symbol | Package offset | Bytes | Upstream source |
| --- | --- | ---: | --- |
| `open_cfw_gx8002_uart_boot_stage2_str_cpu_exception` | `0x82EC` | 19 | `arch/soc/grus/trap_c.c` |
| `open_cfw_gx8002_uart_boot_stage2_str_vreg_dump` | `0x8300` | 12 | `arch/soc/grus/trap_c.c` |
| `open_cfw_gx8002_uart_boot_stage2_str_reg_dump` | `0x830C` | 11 | `arch/soc/grus/trap_c.c` |
| `open_cfw_gx8002_uart_boot_stage2_str_epsr` | `0x8318` | 11 | `arch/soc/grus/trap_c.c` |
| `open_cfw_gx8002_uart_boot_stage2_str_epc` | `0x8324` | 11 | `arch/soc/grus/trap_c.c` |
| `open_cfw_gx8002_uart_boot_stage2_str_pin_set_error` | `0x834C` | 19 | `boards/nationalchip/grus_bk32887_1v/misc_board.c` |

Only the literal string bytes are claimed. In the pinned SDK checkout the
`trap_c.c` printf call sites sit inside `#if 0`, so this window's stock build
was compiled from a different configuration or revision of that file; the
string content is exact, but the surrounding trap-handler control flow in
*this* image is not established by this match and is not reconstructed here.
The `misc_board.c` padmux-init call site is not `#if 0`-gated, but its
surrounding board-init loop is likewise not reconstructed for this
occurrence. Register/vector layout, the trap dispatch code that would call
these format strings, and the padmux board-init loop remain `retained_stock`.

## What remains in `[0x7204, 0x9204)` after CD-006

| Category | Bytes |
| --- | ---: |
| Admitted this pass (`generated_source_data`) | 83 |
| Allocator/comparator code cluster (unattributed, not reconstructed) | 3,358 |
| Duplicate flash-device-name strings (already admitted for a different occurrence; needs a new `stock_occurrences` entry, not new source) | 41 |
| Other unclaimed driver/probe diagnostic strings and two small address tables | ~1,641 |
| U-Boot-derived command-line prompt/help/dispatch strings and command table | GPL-licensed, reuse **not authorized** per `peripheral-oss-library-provenance-audit.md`; blocks source-only closure of this sub-span in software until an exact fork/release is pinned | ~3,069 |

Hardware qualification of every leaf above remains **blocked by unavailable
physical evidence** regardless of source-admission status. This item is not
closed: 8,109 of the 8,192 bytes in `[0x7204, 0x9204)` remain
`retained_stock`.
