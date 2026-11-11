# Bosch interface initializer in C

`r1_bma_interface_initialize` in `native_bma_interface.c` now uses C in
place of naked assembly. Stock entry `0x53aec` returns `0xffffffff` for a
null context. Otherwise it returns zero after eight ordered stores:

| Offset | Width | Value |
| --- | --- | --- |
| 8 | 1 | I2C interface, 1 |
| 36 | 4 | default read callback |
| 40 | 4 | default write callback |
| 4 | 4 | shared bus-address pointer |
| 44 | 4 | delay callback |
| 20 | 2 | transfer length, 64 |
| 13 | 1 | variant, 3 |
| 50 | 1 | performance state, 0 |

REA/Ghidra independently recovers these stores and the null branch. A
volatile device view preserves their widths and order. Registration-only
declarations give the existing callback symbols their pinned Bosch API
types; the native adapters retain their full-word ABI. These declarations
use assembler symbol labels, with no additional implementation, forwarding
function or inline assembly instructions.

Stock/source comparison passes 1,024 scenarios: null and valid contexts
over 256 uniform byte patterns and 256 random context/guard patterns.
It checks the complete ordered write trace, every untouched context byte,
surrounding guards, return values, callee-saved registers, stack and
BASEPRI/PRIMASK. No context reads occur. Function/data pointers are
normalized by symbol role; final firmware placement remains unverified.

The C body is 70 bytes versus the stock 48-byte instruction body. The
read adapter, write adapter and delay retain their previous instruction
bodies. All 562 R1 units compile without failures or duplicate strong
symbols in `build/sources-goal-r1-bma-interface-init-final/report.json`.
Both normal relocatable compositions retain their import sets: 227
application and 34 bootloader imports.

Physical hardware operation, timing, complete fault state, final linking
and whole-image byte identity remain open. No source-plan selection or
G2 workflow gate changed. [Machine-readable evidence](bma-c-interface-init-review.json)
binds source/build/native hashes, REA results and ignored probes under
`build/goal-r1-bma-interface-init/`.
