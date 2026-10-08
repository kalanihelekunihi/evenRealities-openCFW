# UART constructor and actual post-bringup lifecycle

Reconstructed C: `g2/components/bootloader/initializer_callbacks/uart_context.c`, interface `uart_context.h`, original-instruction runner `verify_uart_context.py`. Locked bootloader load `0x410000`, SHA-256 `f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5`. Candidate immutable ELF `67f3f209bc1867dbb2a995e7805dd756105f05bae31831d86e61bda7df689796`; 1,040 direct comparisons PASS, all 1,652 bytes of the eleven listed bodies visited. The focused shared-reset state comparison also passes: three real handles, final row.initialized0, saved-valid1 and UART CFG0. All seven fresh integrated cases PASS on this same immutable image; [exact-image receipt](../same-image-validation-67f3f2.json) also links the affected regressions and 608-input/153-object audit.

| Original body | Source/interface | Instruction bytes |
| --- | --- | ---: |
| `422ad4..422ba8` | post-context constructor | 212 |
| `422ba8..422d20` | existing power guard + new accepted save/restore branch | 376 |
| `422dc6..422e28` | borrowed-buffer activation | 98 |
| `422e28..422ee0` | baud divider and actual-baud output | 186 |
| `42308e..4232c8` | UART configuration | 570 |
| `4236ce..4236fa` | interrupt mask enable | 44 |
| `423700..42372a` | interrupt status clear and readback | 42 |
| `4275ea..427602` | ring descriptor initialize | 24 |
| `41f4f4..41f512` | NVIC ISER write | 30 |
| `41f512..41f530` | NVIC ICPR write | 30 |
| `41f530..41f558` | external/system priority byte write | 40 |

## Constructor and buffer ownership

Four source-owned static contexts occupy `20024400..20024870`, stride `0x11c`. Full-width module >=4 returns5 before null output returns6. A nonzero existing output handle whose flags match `01ea9e06` under `01ffffff` returns7. **The selected pool entry's claim bit is not independently checked:** a caller with output0 or a malformed prior handle can reinitialize an already claimed slot. High flag bits and unmentioned bytes remain intact. The constructor writes magic, module and selected metadata fields in stock order, then publishes the handle last. It neither allocates nor frees.

Activation clears TX/RX enabled bytes first. Each nonzero buffer plus nonzero capacity enables that direction and resets its 24-byte descriptor. A disabled direction retains its previous descriptor; merely clearing its enable byte does not zero its borrowed pointer. Descriptor words are count/read/write0, capacity at+c, element width1 at+10, borrowed pointer at+14. TX descriptor begins context+34; RX descriptor begins+4c. Reactivation discards descriptor counts without freeing or draining anything. Direct tests preserve caller buffer contents for nonaliasing fixtures; aliasing a buffer with context storage cannot imply that storage is untouched.

## Configuration layout and errors

UART module registers are `40039000 + (module << 12)`. Recovered input layout:

| Offset | Width | Meaning from instruction use |
| --- | --- | --- |
| +0 | u32 | requested baud, little-endian |
| +4 | u8 | word-length encoding, low2 bits |
| +5 | u8 | parity0→enable/polarity0;1→enable/polarity1;other→disabled |
| +6 | u8 | stop-bit encoding, low1 bit |
| +7 | u8 | not read by this body |
| +8 | u16 | raw configuration bits ORed into CFG |
| +a/+b | u8/u8 | FIFO threshold encodings, low3 bits each |
| +c | u8 | clock0→class4;1→class6;other rejected |

Configuration first writes CFG0, then ORs8, **before** rejecting an invalid clock. Clock1 also returns6 for revision low byte33. Clock request status is ignored. Baud >=1,500,001 selects higher clock settings and, for revision>=34, sets the module bit in `400201b0`; lower baud clears that bit. Baud clock selectors1..6 map to24/12/6/3/48/49.152 MHz. The helper writes integer/fractional divisors without rounding and reports actual baud in context+30. Invalid selector returns `08000002`; zero integer divisor returns `08000003`, stores actual0, and leaves partial earlier configuration writes intact. `baud<<4` wraps to32 bits; the zero-divisor path is preserved under the fixture's disabled divide trap.

The source division helper specializes the observed 64/32 call contract; it does not claim all original `42287c` entry paths reconstructed. Config0/class4 exercises native denied and allowed clock paths. Config1/class6 exercises its native feature-disabled return path; no PLL-enabled success claim is made here.

## Actual row lifecycle and cleanup boundary

The existing row loop `41f612` now receives real handles for rows 1/2/3 (`2002451c`, `20024638`, `20024754`). Its sequence is constructor → register configuration → power enter(op0,save0) → UART config → borrowed-buffer activation → NVIC clear pending → priority → NVIC enable → UART interrupt mask OR `471` → row initialized1 → existing callback `41f8ba`.

[Focused shared reset comparison](../uart-startup-state-67f3f2.json) verifies all four row values, all 1,136 context-pool bytes, UART registers, ordered writes, clock ownership and native visit counts at the real row-loop return. Row 3 borrows a1,024-byte TX buffer at `20080800` and enables only TX; rows1/2 enable neither direction.

That last callback **clears row.initialized back to0**, updates the two pin/register IDs, and invokes power transfer(op2,save1). It is not a no-op initialized-record notification. Transfer saves UART registers20/24/28/2c/30/34/38/48 into context+8..24, marks saved-valid1, releases the clock, clears all pending UART status via write44/read40, writes CFG0, and leaves the power domain. Power/clock status is ignored. Restore(op0,save1) requires saved-valid or returns7; it restores the eight words in order and clears the marker, even if clock/power calls report failure. Operations1 and2 share the save/down path; operation is full32 bits while save is low8 bits.

This is register snapshot/power bookkeeping, **not proven TX/RX completion, DMA stop, task/IRQ drain, callback quiescence or memory release**. Interrupt clear writes ICR44 then reads MIS40; it does not clear the enable mask38. Existing generic helper names `post_enable` and `post_precommit` are retained ABI names: their actual NVIC destinations are respectively `e000e280` (clear pending) and `e000e100` (enable).

## Store-width comparison repair

The first integrated run failed peripheral comparison because the old recorder retained `value & ffffffff` even for one-byte stores. The newly observed NVIC priority range includes the existing NOR helper `41fdde` / `nor_mspi_init/hal_leaves.c`: at `e000e420`, stock register value `ff0` and source register value `f0` both store byte `f0`. [Focused original/source memory evidence](store-width-evidence.json) verifies that existing helper at `e000e420` and the new UART helper at `e000e410` (whose raw values already agree). The recorder now masks to `size*8` bits, preserving all actual transferred bytes and write ordering; it does not suppress peripheral differences. Raw failed-run evidence and the prior input-hash manifest remain in the snapshot. Final seven-case runs use the corrected recorder.

## Validation limits and practical implications

[Direct receipt](../uart-context-67f3f2.json) links all case labels, byte-verified original trace, source/image hashes and full observations in the immutable snapshot. Tests compare return values, ordered writes, UART reads, all four context bytes, buffer contents, registers, clock ownership and PRIMASK. No success return stubs replace the eleven bodies or their native power/class4 clock children. Only absent resident ROM40 cycle wait is controlled. Peripheral/NVIC state is mapped RAM, power acknowledgement fixed; no silicon timing, IRQ delivery or scheduling is demonstrated. Context modules0..3 are the constructor-established domain; corrupted accepted handles with arbitrary module words are outside the demonstrated domain.

For source work, preserve selective initialization, existing-output error precedence, partial writes on error and ignored child statuses. For CFW/apps, do not infer active UART service from constructor success or row.initialized, and keep buffers alive while the borrowed descriptors may be used. An owned-buffer or shutdown patch still needs the real TX/RX/DMA/IRQ consumption and drain paths; this batch does not authorize or implement such a patch.
