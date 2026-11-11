# QMA identity/layout and range entries in C

`r1_qma6100_configure_boundary` and `r1_qma_range` now use ordinary C
instead of naked assembly in `native_qma_configuration.c`. REA/Ghidra,
native instructions and execution establish both entry contracts.

Configuration entry `0x86e68` clears the ID byte and tries state-address
values `0x12` then `0x13`, storing each probe's low ID byte. The loop stops
for a full result equal to `0xfa` or with full-word high nibble test
`id >> 4 == 9`. After exhaustion, the final check uses the low-byte high
nibble. This distinction is preserved for full-word probe results. A
recognized ID calls setup with the rate's low byte and returns its full
result; otherwise the entry returns zero.

Regardless of identification or setup failure, the entry clears state
offset eight and writes three map halfwords followed by three sign
halfwords. Defaults are read live after callbacks from native address
`0x9a6a6`, preserving each read/store width and order. The distinct
transport runtime address is not changed by these state-address writes.

Range entry `0x87188` stores a four-byte scale at state offset four:
2 selects 2048, 4 selects 1024, 8 selects 512, 15 selects 256 and every
other full-word value selects 4096. It then tail-calls write-retry with
register `0x0f` and the original range, returning that result. REA infers
a void return here; instructions and execution establish the R0 result.

Stock/source comparison passes 3,224 scenarios covering every first ID
byte with several second IDs, all byte rate/range values, full-word
classification edges, errors, callback changes to state/default data and
interrupt masks. Probes compare ordered context/default accesses,
arguments, stopping points, returns, all state/guard bytes, callee-saved
registers, restored stack and masks. The range write observes original
SP/LR, confirming tail behavior. Default-data mutation is fault injection,
not a claim that stock flash is writable. Callbacks are modeled and
clobber caller-saved registers/flags.

| Entry | Stock bytes | C bytes |
| --- | --- | --- |
| Identity/layout configuration | 110 | 114 |
| Range setter | 56 | 60 |

The setup argument now has a proper C declaration; its instruction body
and the other configuration helper bodies remain unchanged. All 562 R1
units compile without failures or duplicate strong symbols in
`build/sources-goal-r1-qma-layout/report.json`; imports remain 227
application and 34 bootloader.

Controlled state placement at `0x2001e4b0` does not establish final layout.
Physical operation, timing, complete fault state, final linking and byte
identity remain unverified. No source-plan selection or G2 workflow gate
changed. [Machine-readable evidence](qma-c-layout-review.json) binds source,
manifest, build/native hashes, REA observations and ignored probes under
`build/goal-r1-qma-layout/`.

The later [setup review](qma-c-setup-review.md) replaces setup with C and
validates the regenerated identity/layout caller with the actual setup body.
