# Native motion cache boundaries in C

Current implementation: [ordinary C motion IRQ cache ABI](motion-cache-pure-c-review.md). R4/frame observations described below have been retired.

Stock bus lookup `0x50150` already has one C implementation,
`r1_motion_bus_device_bind`, but the frontier did not associate it with that
entry. The mapping is corrected without adding an alias or another owner.
The existing bus cell remains at `0x200076b4`, and the existing IRQ cell remains
at `0x200076b0`.

The bus lookup is now explicitly noninline, matching the call from IRQ lookup
`0x50128`. The IRQ lookup retains incoming R4 until that call completes, then
holds the native context base `0x200076a8` and accesses the IRQ cell at offset
8. Empty register constraints preserve this provider-visible state. Integer
address arithmetic does not introduce ownership of the preceding context bytes.
Both functions still use the existing volatile cache owners and registry.

The direct bus provider frame remains eight bytes; when called through the IRQ
lookup its native depth is 16 bytes, restored from the former inlined depth of
8. The IRQ provider frame is eight bytes, with R4 equal to the native context
base rather than the standalone IRQ cell address.

The product chain passes 1,296 paired sequences of three invocations, or 3,888
paired invocations. Cases cover cold/warm/null/all-ones caches, null lookup
results and retries, other-cache mutations during lookup and overwritten own
cells before provider return. Tests compare ordered cache/saved-frame accesses,
provider R4–R11 and depths, return values, final caches, preserved registers and
interrupt masks. Nested private LR words are normalized. Guard bytes before
the cells remain unchanged and are never accessed. The old inlined object,
wrong context base, wrong bus name and missing IRQ store are rejected.

All 583 R1 units compile. The 582 other objects, manifest, imports, exports,
owned data, and every other function section/relocation in this unit remain
unchanged, including the standalone bus implementation. Qualification selects
no exact regions; compiled instruction encodings still differ. The source plan
and canonical hybrid hash remain unchanged at 4,155 source-built bytes.
Registry providers are modeled; caller-clobbered registers/flags except R0,
arbitrary aliases/faults/concurrency, electrical/driver behavior and complete
source-only rebuilding remain unproven. Probes, REA evidence and audit are under
`build/goal-r1-motion-cache-c`; durable results are in the adjacent JSON.
