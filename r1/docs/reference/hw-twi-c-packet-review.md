# Hardware TWI packet policy in C

`board/native_hw_twi_operations.c` now implements packet dispatch, provider
calls, timeout selection, result truncation and status mapping in C. The old
assembly loaded a temporary five-word call plan, dispatched providers and
waits, and mapped results across several branches. Each of the four exported
entry points now needs only a 10-byte ABI bridge. Their combined assembly
shrinks from 228 to 40 bytes. No executable opcode array or retained binary
replacement was introduced.

The bridges retain stock saved-word frames: read exposes saved R3 at entry
SP minus 8; write exposes saved R2/R3 at SP minus 16/12. Read and bulk write
place the instance in the first saved word. Single-byte write replaces only
the low two bytes of the saved R3 word with register/value, retaining its
upper halfword, and zeroes the saved R2 word. C passes the fifth provider
argument normally, preserving its value. Compiler-private stack placement
below these explicit frames differs from stock.

REA and raw instructions cover primary read `0x55414`, primary write
`0x55ce0` and secondary write `0x55d50`. Raw disassembly also covers secondary
read `0x55448`. The stock initialized operation table independently identifies
these entries. Primary uses halfword register/length fields; secondary uses
byte fields where shown by stock. Single-byte writes wait only when TX returns
full-width zero, then map the low byte of the resulting status. Thus TX
`0x100` skips the wait and maps to success, matching stock. Bulk status mapping
uses the full word. Primary/secondary single-byte timeouts remain 500/100.

There are 3,168 direct stock/C comparisons with modeled register-transfer,
TX and wait boundaries. They cover null packets, closed/open buses, boundary
lengths and register fields, full-width result patterns, unaligned packet
addresses, and controlled mutation of native saved words by providers.
A further 2,112 comparisons execute the actual register-transfer adapters
alongside the packet code. Only Nordic TX/RX and wait providers are modeled
in that set; modeled RX writes also exercise output-memory comparisons.
Both sets additionally compare the previous source implementation with stock.

Checks cover raw R0, saved-register results, provider arguments and transfer
bytes, cluster state, guards, R4-R11, SP, interrupt masks and callback alignment.
All 562 R1 units compile, with zero failures or duplicate strong symbols.
Imports remain 211 application / 34 bootloader; the other 561 source units
are unchanged and `make sources-check` passes. The source plan and G2 workflow
are unchanged by this packet rewrite.

This is bounded execution evidence, not native byte qualification, physical
I2C/IRQ validation, concurrency or fault equivalence, final firmware linking,
or complete source readiness. Exact inputs and hashes are in the
[machine-readable review](hw-twi-c-packet-review.json).

The subsequent [packet-write C review](twi-packet-write-c-review.md) removes both packet-write bridges and their helper kernels while preserving the 16-byte frame. Packet read paths and register-write adapters remain unchanged.
