# Bosch device initializer in C

`r1_bma456w_initialize` in `native_bma_initialize.c` now uses ordinary C
instead of naked assembly. Stock entry `0x543c4` snapshots eight bytes from
`0x9a768` before calling the lower device initializer. It propagates a
nonzero status unchanged, returns `0xfffffffc` when a successful call
leaves chip ID other than `0x16`, and otherwise performs five stores:
resolution 16 at offset 12, feature length 76 at offset 22, config size
5016 at offset 48, and the six remap bytes at offsets 29 and 33.
REA/Ghidra confirms the branches and resulting field values.

Packed may-alias word/halfword views express the native unaligned
four-byte and two-byte remap stores. Volatile accesses preserve the
pre-call pair of four-byte literal reads, the post-call chip-ID byte read,
and the exact field-write widths and order. The existing eight-byte data
span remains `000102000000802e`: six attributed Bosch remap bytes and two
following bytes whose origin remains gated. No executable blob is added.

Stock/source comparison passes 796 scenarios, including every chip-ID
byte, full-width error returns, randomized context/guard bytes, null
contexts on failing lower calls and interrupt-mask combinations. A probe
changes the literal during the lower callback to verify the pre-call
snapshot is used; this is fault injection, not a claim that stock flash
is writable. Ordered literal/device accesses, returns, all context and
guard bytes, callee-saved registers, stack restoration and masks match.
The lower initializer is mocked and clobbers caller-saved registers.

The C body is 62 bytes versus 64 stock bytes. Both callback frames use
SP-16 with eight-byte alignment; private spill contents are unverified.
The lower initializer receives a proper C parameter declaration, and its
instruction body and the configuration wrapper's body remain unchanged.
Both still contain assembly.

All 562 R1 units compile without failures or duplicate strong symbols in
`build/sources-goal-r1-bma-device-init-verified/report.json`; import sets
remain 227 application and 34 bootloader. Physical sensor operation,
timing, complete fault state, final linking and byte identity remain open.
No source-plan selection or G2 workflow gate changed.

[Machine-readable evidence](bma-c-device-init-review.json) binds source,
manifest, build/native hashes, REA results and ignored probes under
`build/goal-r1-bma-device-init/`.

The later [core-initializer review](bma-c-core-init-review.md) replaces the
lower initializer with C and verifies both initializers together.
