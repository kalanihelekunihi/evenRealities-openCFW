# Bosch default bus adapters in C

The read and write adapters in `native_bma_interface.c` now use ordinary C
instead of naked assembly. Stock entries `0x53ab4` and `0x53ad0`, each 28
bytes, read one unsigned address byte from the interface handle, preserve
the full register argument and data pointer, truncate length to 16 bits,
and invoke the corresponding motion-bus request. A nonzero request result
returns zero; a zero result returns the full word `0xfffffffe`.
REA/Ghidra independently recovers that behavior for both stock entries.

The C signatures describe the native adapter's full register/error words;
they do not narrow the register or result to the pinned API's callback
byte types. A volatile byte load preserves the handle access width before
the request. The request functions already implement their own transfer
and address handling; these adapters add no validation or retries.

Stock/source comparison passes 2,176 scenarios, covering every address
byte, zero and boundary lengths through `0xffffffff`, full-width register
values, null data forwarding, zero and several nonzero bus results, and
BASEPRI/PRIMASK combinations. Ordered handle reads and request arguments,
return values, callee-saved registers, restored stack and interrupt masks
match. Both callbacks enter with eight-byte stack alignment and an
eight-byte frame; modeled callbacks clobber caller-saved registers.

Each C body is 30 bytes, compared with 28 stock bytes. The delay and
interface-initializer compiled bodies are unchanged. All 562 R1 units
compile without failures or duplicate strong symbols, and both normal
relocatable compositions retain their import sets: 227 application and
34 bootloader imports. The report is
`build/sources-goal-r1-bma-bus-adapters/report.json`.

The underlying bus request is mocked here. Physical bus operation,
timing, complete fault state, private spill contents, final linking and
whole-image byte identity remain unverified. No source-plan selection or
G2 workflow gate changed. [Machine-readable evidence](bma-c-bus-adapters-review.json)
binds source/build/native hashes, REA observations and ignored probes under
`build/goal-r1-bma-bus-adapters/`.
