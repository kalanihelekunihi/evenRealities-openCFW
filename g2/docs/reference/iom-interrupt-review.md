# Apollo IOM interrupt and DMA review

This bounded review uses the locked 2.2.6.10 Apollo main payload and REA's
Ghidra 12.1.4 provider. It checks existing C in
`g2/src/apollo-main/hal/iom/am_hal_iom_interrupt.c`; it does not admit new
workflow coverage, constitute independent review, or pass a reconstruction gate.
Raw pseudocode, disassembly, observed body ranges, analysis profile and query
limitations are retained in
[`iom-interrupt-rea-review.json`](../../evidence/iom-interrupt-rea-review.json).

## Observed bodies

| Entry | Inclusive body | Bytes |
| --- | --- | ---: |
| DMA programming | 0x55C174–0x55C1DF | 108 |
| Interrupt enable | 0x55C498–0x55C4CF | 56 |
| Interrupt status | 0x55C4D0–0x55C513 | 68 |
| Interrupt clear | 0x55C518–0x55C545 | 46 |
| Interrupt service | 0x55C558–0x55C7DF | 648 |

The analysis-only ELF wraps unchanged stock bytes from runtime
`[0x55BD70,0x55CF40)` with analyst supplied Thumb symbols. Its section was
checked against the original payload using VA = file offset + 0x437FE0.
Entry symbols and declared sizes seed analysis; they are not independent
function-boundary discovery. The wrapper is an ignored experiment under
`build/rea-iom-hardware/`, never a firmware build input.

## MMIO semantics lost in raw pseudocode

The standalone clear function validates the handle before touching MMIO:
NULL or `(prefix & 0x01FFFFFF) != 0x01123456` returns 2. For a valid handle,
its instruction-backed pseudocode is:

```text
module := load_u32(handle + 4)
base := 0x40050000 + module * 0x1000    // 32-bit arithmetic
store_volatile_u32(base + 0x208, mask) // INTCLR, instruction 0x55C536
discard load_volatile_u32(base + 0x204)// INTSTAT, instruction 0x55C53E
return 0
```

Both the older corpus export and this fresh REA decompilation omit the
discarded load. Disassembly retains it, and the existing C correctly uses a
volatile read. A raw decompiler export therefore cannot establish complete
hardware pseudocode even for this small function.

The service function's queue-drain path instead writes INTEN=0, then
INTCLR=0xFFFFFFFF, then restores the user's INTEN at 0x55C7BE, 0x55C7CA and
0x55C7D4. There is no intervening INTSTAT load. Adding one to that path to
generalize the standalone helper would change stock memory effects.

DMA programming wraps `last_hp_idx + 1` as u32 before unsigned modulo
`max_hp`. It writes OFFSETHI, DEVCFG, DMACFG=0, DMATOTCOUNT, DMATARGADDR,
DMACFG and CMD, in that order. The helper contains no divisor or handle check;
caller invariants remain part of the outstanding behavioral review.

## Focused stock/C execution comparison

An isolated Unicorn probe compared the original Thumb instructions with the
existing C compiled by Clang for Cortex-M55, hard float, `-Oz`, freestanding.
All **136 cases passed**, comparing return values, output memory, and the
ordered MMIO read/write trace across IOM modules 0–7:

- Enable: invalid and NULL handles, zero mask, forbidden threshold bit,
  high-bit mask and all bits set.
- Status: invalid and NULL handles, raw and enabled-only status (including
  a noncanonical true byte 0xFF), and NULL output.
- Clear: invalid and NULL handles, zero and all-bit masks. The trace includes
  the otherwise discarded INTSTAT read.
- DMA programming: u32 index wrap from 0xFFFFFFFF to 0 with a three-entry queue.

A second probe passed **111 service comparisons** across modules 0, 4 and 7.
It covers invalid/NULL handles; high-priority command/DMA completion and
error combinations; DMA disabled/enabled; queue drain and continuation;
callback-driven restart; sequence-mode callback retention; command-queue
status failure; absent command queue; and callback-index wrap at 255 and
0xFFFFFFFF. It compares return status, the entire 0x858-byte handle prefix,
three DMA queue entries, ordered MMIO events, and helper/callback arguments
and order. Helper calls and callbacks are intercepted with controlled mocks;
this tests the service routine's boundary behavior, not those helpers.

Probes, compiled artifacts and per-case traces are under
`build/rea-iom-hardware/`. Neither probe verifies interrupt concurrency,
peripheral timing, or physical hardware. Register memory is a passive
emulator mapping. Matching MMIO traces does not demonstrate peripheral side
effects or byte identity of compiled C. Trace/probe digests and case
summaries are retained in the evidence JSON.

REA reports partial call coverage for the service function: three callback
sites have unknown runtime targets; two direct call sites leave the imported
slice (0x53901A and 0x5390FC), and two call 0x55BD70, which was not recognized
as a function in this import. Its decompiler also reports four apparent parameters
because the prologue saves r0–r3 as scratch/status storage; this does not
establish a four-argument public ABI. Global target reconciliation and
independent pseudocode review remain outstanding.
