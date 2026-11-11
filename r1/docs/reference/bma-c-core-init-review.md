# Bosch core initializer in C

`r1_bma4_initialize` in `native_bma_initialize.c` now uses ordinary C
instead of naked assembly. Stock entry `0x5447e` checks the device first
and propagates failure. It sets dummy-byte count to one for SPI, performs
an extra register-zero read, and proceeds only on success. Other interfaces
set dummy-byte count to zero. The final register-zero read writes the
stored chip ID only when successful; transport errors propagate unchanged.

Two separate zero-initialized output bytes preserve the actual and dummy
read boundaries. The interface decision is captured before the first read;
callbacks may change the context, but no additional interface test or
dummy-byte reset occurs between SPI reads. A volatile context view
preserves the accessed field widths and order.

REA/Ghidra recovers the branches, two initialized scratch bytes and
conditional chip-ID store. Its inferred return type is `void`; that is a
decompiler artifact. Native instructions and execution establish the
status returned in R0, including full-width transport status propagation.

Stock/source comparison passes 2,048 scenarios: 1,024 direct core calls
and 1,024 combined calls through the actual C device initializer. The
actual compiled device checker executes in both sets. Coverage includes
every chip-ID byte, SPI and non-SPI paths, failed first/second reads,
missing callbacks, null devices, partial/no-write outputs, and callback
changes to chip ID, interface and dummy count. Traces verify separate
scratch pointers, zero initial output bytes, ordered context accesses,
return status, all context/guard bytes, callee-saved registers, restored
stack and interrupt masks. The register-read boundary is mocked and
clobbers caller-saved registers.

The C core body is 84 bytes versus 74 stock bytes. The outer initializer
remains 62 bytes. Direct read callbacks use native SP-24 versus C SP-16;
combined callbacks use native SP-40 versus C SP-32, all eight-byte aligned.
Surrounding saved scratch bytes and private spills are not reproduced.
The configuration wrapper's instruction body remains unchanged and still
contains assembly.

All 562 R1 units compile without failures or duplicate strong symbols in
`build/sources-goal-r1-bma-core-init/report.json`. Normal import sets remain
227 application and 34 bootloader. Physical bus operation, timing,
complete fault state, final linking and byte identity remain unverified.
No source-plan selection or G2 workflow gate changed.

[Machine-readable evidence](bma-c-core-init-review.json) binds source,
manifest, checker object, build/native hashes, REA observations and ignored
probes under `build/goal-r1-bma-core-init/`.

The later [configuration review](bma-c-config-review.md) replaces the last
assembly wrapper in this file with C.
