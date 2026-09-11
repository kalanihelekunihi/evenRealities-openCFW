# GX8002 UART boot stage 2 reset window (CD-003)

Scope: package `[0x2850, 0x31E4)`, 2,452 retained bytes, the first slice of
the authenticated UART boot stage 2 envelope (`gx8002-uart-boot-stage2-boundary.md`
covers the full `[0x2850, 0x958C)` typed-provider boundary). Runtime
`0x10002800..0x10003194` — the codec IRAM load address through the reset
handler and its immediate callees. This document narrows that boundary with
named, individually qualified leaves; it does not change the typed-provider
boundary's own claims.

## Layout established by disassembly

The C-SKY toolchain disassembles raw stock bytes correctly only once the
object carries the SDK's own ELF `e_flags` (`0x21006009`); wrapping the slice
with `csky-unknown-elf-objcopy -I binary -O elf32-csky-little -B csky` and
patching `e_flags` at file offset 0x24 before disassembly, `--adjust-vma`'d
to the runtime load address, reproduces the same instruction stream GCC would
read back from its own compiled objects. Without the patched flags, objdump
silently misdecodes 32-bit C-SKY V2 instructions as pairs of unrelated
16-bit ones.

| Runtime range | Bytes | Content |
| --- | ---: | --- |
| `0x10002800..0x10002900` | 256 | Vector table: 32 words of `0x10002900` (reset), 32 words of `0x10003124` (shared default handler) |
| `0x10002900..0x10002922` | 34 | Reset entry: set VBR (`mtcr cr<0,0>`=`0x80000200`), clear PSR bit 3, set SP=`0x2000e7fc`, `bsr` to three callees outside this window (`0x10005100`, `0x100052b0`, `0x100054e0`), then `br` self (idle) |
| `0x10002924..0x1000292C` | 8 | Literal pool for the reset entry (`0x80000200`, `0x2000e7fc`) |
| `0x1000292C..0x10002944` | 24 | Word-wise BSS-clear loop over `[0x2000953c, 0x2000a1fc)`, same shape as `runtime_gx8002_clear_bss.c`'s other occurrence but distinct bounds |
| `0x10002948..0x10002950` | 8 | Literal pool for the BSS-clear loop |
| `0x10002950..~0x100029F8` | ~168 | Exception-frame builder: `psrset ee`, saves r13/r15/cr2/cr4 into a stack frame, calls `0x100051a4`, loops back to its own entry (`br 0x10002950`) |
| beyond | remainder | UART/analog/IRQ configuration glue, including three exact NationalChip lvp_kws matches (below), interleaved with code not yet attributed |

None of the `bsr` targets above (`0x10005100`, `0x100052b0`, `0x100054e0`,
`0x100051a4`) fall inside this 2,452-byte window; they are out of scope for
CD-003.

## Exact upstream object matches in this window

`gx8002-upstream-object-candidates.json`'s SHA-256 section matcher already
named three exact matches against the pinned NationalChip `lvp_kws` SDK
(commit `8bf9ee5cb6eeb226011e61c15fa4981b83b93bd5`, MIT) inside `[0x2850,
0x31E4)`:

| Symbol | Package offset | Bytes | Object |
| --- | --- | ---: | --- |
| `gx_analog_config_update_enable` | `0x2A8C` | 20 | `drivers_lib/misc/grus/misc.o` |
| `dw_uart_getc` | `0x2F1E` | 22 | `drivers_lib/serial/dw_uart.o` |
| `csi_vic_enable_irq` | `0x311C` | 28 | `drivers_lib/intc/vic.o` |

These were candidates only (no source, no production route). CD-003 admits
two of the three:

### `gx_analog_config_update_enable` — admitted, byte-exact

No `.c` body exists in the SDK checkout (only the compiled object and the
`include/driver/misc.h` declaration/doc-comment). Disassembly shows four
32-bit MMIO stores of the literal `89` to `0xa0005040/44/48/4c` and a `rts`;
`runtime_gx8002_analog_config_update_enable.c` reproduces this directly.
`verify_gx8002_analog_config_update_enable.py` compiles it with the codec's
usual `-O2 -mcpu=ck804ef -mhard-float ...` flags and requires the compiled
`.text` section equal the stock envelope byte for byte — confirmed at every
tested optimization level (`-O1`..`-O3`, `-Os`). Package offset `0x2A8C` is
4-byte aligned, so it fits the candidate pipeline's placement contract.

### `csi_vic_enable_irq` — admitted as a second occurrence, instruction-equivalent

`runtime_gx8002_irq.c`'s existing `open_cfw_gx8002_irq_enable` (a `noinline`
wrapper around the pinned Apache-2.0 C-SKY CSI `csi_vic_enable_irq()`) is
already qualified against one main-image occurrence (package `0x174c0`, see
`verify_gx8002_irq.py`). The stock UART boot stage 2 image independently
compiles the same source body again at `0x311C`, with different register
allocation (24 compiled bytes vs. a 28-byte envelope; stock uses a
three-operand `lsl` and computes the VIC index before the shift value, the
candidate the reverse). `verify_gx8002_irq_boot_stage2_enable.py` decodes
both and proves, for 269 tested `IRQn` values (0..259, boundary bits, negative
and maximum `int32_t`), that both compute the identical
`VIC->ISER[(IRQn>>5)&3] = 1<<(IRQn&31)` write — no byte-equality claim, only
proven instruction-level equivalence with consistent register renaming, the
project's established bar for this style of admission (see the analog/I2S/VAD
tranches). Package offset `0x311C` is 4-byte aligned.

### `dw_uart_getc` — not admitted; alignment gap, not a missing reconstruction

`runtime_gx8002_uart_receive_byte.c` already exists, is already qualified
against two other occurrences (`0xc7ec`, and a relocated XIP copy at
`0x10203260`; see `verify_gx8002_uart_receive_byte.py` /
`verify_gx8002_uart_receive_byte_relocated.py`), and its compiled section is
confirmed **byte-for-byte identical** to the 22 stock bytes at `0x2F1E`
(`419022e41300609163e4012003e9fdff009200743c78`). It is not wired into
`build_gx8002_source_candidate.py`'s ownership pipeline at all yet (neither
its existing two occurrences nor this one), and this third occurrence cannot
be added through the existing mechanism regardless: `0x2F1E mod 4 == 2`, and
`build_gx8002_source_candidate.reviewed_replacements()` requires
`package_offset % section['align'] == 0` where `section['align']` is the
compiled `.text` section's ELF `sh_addralign`, which C-SKY GCC always sets to
4 for executable sections (confirmed across `-O0`..`-O3`,
`-falign-functions=2` does not change it). Every `compiled_c`/
`compiled_assembly` occurrence presently in the ownership ledger is 4-aligned;
none is 2-aligned. Widening that alignment check is a change to shared
verification infrastructure used by ~230 other occurrences and is out of
scope for this single work item. **Follow-up**: either loosen
`reviewed_replacements()`'s alignment check to the compiled function's actual
minimum required alignment (2, for these leaf functions with no literal pool
access wider than a word) with a dedicated test proving no misaligned access
results, or accept this specific 22 bytes as a documented, permanently
retained residual with a `NOASSERTION`-free citation to the byte-exact source
match above (source identity is proven; only the integration mechanism is
missing).

## What remains in `[0x2850, 0x31E4)` after CD-003

| Category | Bytes |
| --- | ---: |
| Admitted this pass (`compiled_c`, both leaves) | 48 |
| Named-and-source-identical but not yet integrated (`dw_uart_getc`) | 22 |
| Vector table (source-authorable data, not yet integrated) | 256 |
| Reset entry + its literal pool | 42 |
| BSS-clear loop + its literal pool | 32 |
| Exception-frame builder and remaining unattributed glue | remainder (~2,052) |

Hardware qualification of every leaf above remains **blocked by unavailable
physical evidence** regardless of source-admission status.
