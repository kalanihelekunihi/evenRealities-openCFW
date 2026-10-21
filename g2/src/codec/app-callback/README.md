# Experimental GX8002 app callback C candidates

`callbacks.c` implements two authenticated XIP child helper bodies:
`0x1020975c` prepares and dispatches `(1,12,event_argument)`, and
`0x10209770` writes a 28-byte request structure and invokes a child consumer.
The source is the native instruction listing and Ghidra pseudocode retained
under `pre-consolidation:g2/analysis/shortcut-csky-authenticated-20261009-agent1/final-source-boundary/`.
The public NationalChip sample does not provide these firmware-specific bodies.

This file compiled using the retained GCC 6.3.0 C-SKY toolchain with
`-mcpu=ck804ef -mhard-float -O2`. Product global storage and three lower
functions remain unresolved. The request contains a pointer to a local byte;
its consumer and queue must establish the pointer lifetime. That lower behavior
and the global request location have not been proven. The object is not linked
into a firmware image and is not an equality claim.

`board_uart.c` additionally reduces five retained XIP pseudocode bodies:
board getter/gain lookup, DMA burst enumeration, UART transmit and receive.
It compiles for the same C-SKY target with 32-bit structure-offset assertions.
Native instruction review establishes the board address and nine signed dB
gain values, now explicitly defined as C constants; final placement remains open. The UART polling loops preserve their blocking behavior and volatile
MMIO access. These new bodies have compilation and static native instruction evidence;
producing ABI, original-byte execution, concurrent MMIO behavior and physical hardware remain
unverified. Provenance is in `pre-consolidation:g2/analysis/c-source-completion-20261011/codec/board-uart-receipt.json`.

Three more C bodies now reduce event timestamp preparation, event reply
construction, and GPIO output at0x102093dc/0x102093f4/0x10205f88. Independent
native review establishes the actual fixed request address0x20026d5c and
RAM timestamp/reply slots, including16-bit reply truncation and return0. GPIO
reads/modifies/writes0xa0001004 with a five-bit pin index. Timestamp resident
interface and request consumer remain unresolved; their state/electrical
effects are not replaced by guessed values. The codec graph now has29 exports
and two imports; its whole-image coverage remains unestablished. See
`codec/event-native-review.json` for static evidence and build hashes.

## Request/queue/CRC source round

The request consumer, fixed channel lookup and queue-full body are C source.
The unchanged pinned NationalChip CRC implementation matches all 256 stock
table words; 1,460 host comparisons pass against independent zlib. This is
not original C-SKY execution. Recovered mixed-width accesses compile with
explicit `-fno-strict-aliasing`.

`uart_message_start.c` adds the native 0x10207adc control-flow body, preserving
word stores, return values and call order. Its queue, timer, channel and
callback lower contracts remain explicit. Stock callback identity 0x10207f08
is retained pending source/layout ownership; it is not a flashable linkage.
Historical export/import counts above describe earlier snapshots.

The subsequent channel-runtime round compiles 41 providers with five real
resident imports: critical save/restore, header sync, queue enqueue, timestamp.
Decoded callback-set, stop and timer-start bodies preserve ordered SRAM/MMIO
operations. Timer-start keeps the native shift mnemonic for exceptional
inputs rather than introducing undefined C shift expressions. Source-owned
initialization/layout and target execution remain unqualified.
