# CASE remaining direct-provider frontier

The fixed CASE image is `g2-2.2.6.10/firmware_box.bin`, SHA-256
`36ca0c13558f252af286ae2b36b5e576d087d21d37b15d778e7da9f502a70374`.
This pass rechecked the four remaining direct import names against the
retained Ghidra corpus and exact Thumb disassembly. It did **not** add a
source unit or change the candidate archive. The archive receipt remains
**37 objects, 61 provided symbols, 5 unresolved imports**, SHA-256
`7b26065eb1ae19f242b5a387559e322285f5f34f30e408da68cc9a880cfa9a00`.
The original 12-name direct tally remains **8 complete, 4 open**; lower
formatter `case_vformat` is the fifth unresolved import.

## UART IRQ and DMA split points

`case_uart_other_irq` and `case_uart_dma_boundary` are source-candidate
split names introduced by the bounded prefix in
`uart_error_atomic_offline/uart.c`; neither is a standalone stock symbol
with a function-entry ABI. The one stock handler starts at `0x08005f50`.
The prior 6,768-case comparator executes the selected RX/error prefix and
stops at the stock continuation `0x08006086` for other IRQ handling; DMAR
was disabled in that suite. The authenticated disassembly retained here
shows the DMA error path at `0x08006014..0x08006070` and other-IRQ tail
`0x08006086..0x08006230`.

The DMA path clears CR3.DMAR under PRIMASK, reads the UART DMA handle at
offset `0x80`, writes an abort callback at DMA offset `0x38`, and calls
`0x080048e6` before either returning or invoking that callback. The
other-IRQ tail branches across TOIDLE, receive timeout, TX-ready,
transmit-complete, CTS and indirect RX/TX callback paths; it includes
PRIMASK-protected CR1/CR3 writes and DMA count/state reads. A C function
that merely accepts the UART handle cannot be claimed equivalent to this
continuation without showing how the stock entry's saved ISR/CR1/CR3
snapshot and register state map into that call.

The next discriminating test is a full-handler original/source comparator
that starts both sides at the public IRQ entry, with coherent DMA handles,
callback pointers, peripheral ISR transitions and PRIMASK trace checks.
It must exercise all listed tail families and source-own the DMA abort
callback/`0x080048e6` contract or retain it as an explicit lower boundary.
Until then, filling either split import with a stub or a selected-branch
helper would conceal the untested stock behavior. The retained
`irq-original-disassembly.txt` is the exact `0x08005f50..0x08006230` slice
from the hash-guarded image.

## Product command dispatch

`case_legacy_command` maps to stock `0x08000928`, with a byte-offset jump
table immediately after the BL at `0x08000940` and power, reset, peripheral
and logging branches. The decompiler reported unresolved jump-table recovery;
`case-command-switch-frontier-20261010` now decodes all 16 entries and ten
distinct targets through the authenticated Thumb-1 helper at `0x08009190`.
A complete body still requires every reachable command case, with
argument/side-effect oracles for the child calls and nonreturning reset or
standby paths.

`case_binary_command` maps to stock `0x08000e1c`. Its retained body covers
binary framing/length checks and many command-specific sensor, aging,
output, power, logging and event paths. Existing source modules cover
selected local children but do not cover the full dispatch. The next test
must enumerate actual command opcodes/length formats and reach every
branch, including bounded nonreturning hardware actions, before integrating
a complete C body.

The lower formatter at `0x08009210` remains separately open; current
logger wrapper tests stop at that call. No source-equivalent formatter or
physical UART/logger output is claimed here. These five unresolved names
are **not five equal-effort implementations**. Source archive composition,
CASE startup/link, coherent product state, and device behavior remain
separate gates.
