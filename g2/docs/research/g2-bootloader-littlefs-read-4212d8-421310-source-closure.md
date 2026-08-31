# G2 bootloader LittleFS block-read callback source closure

> **Superseded temple-status premise:** Treat temple nonresponse/unavailability
> claims below only as history. The case was bumped during lunch and caused the
> disconnect, not firmware or flashing; exclude it from feasibility conclusions.
> Hardware testing remains blocked by unavailable physical evidence.

## Disposition

The complete authenticated callback `[0x004212D8,0x00421310)` is implemented
as freestanding clean-room C in
`components/bootloader/core_overlay/runtime_littlefs_read_4212d8.c` and is
production-routed under both reviewed compiler profiles. This closes the
callback software body; it does not validate physical flash reads or establish
firmware-wide functional completeness.

## Authenticated boundary and ABI

- Stock callback: 56 bytes, SHA-256
  `26e2b4b9fe7f3389d15261fe01621eb3b37bfc4b9923ebfac70609216ac92a90`.
- Successor program callback `[0x00421310,0x00421348)`: 56 bytes, SHA-256
  `6d46e88d2df85850b8ec35b4f55e5e0522884210c8bf5a3419e328599ffebf60`.
- Configuration object: `0x00431070`; its read field is `0x004212D9`.
- Source-owned guarded reader: stock entry `0x00420F70`.
- Source-owned logging dispatcher: stock entry `0x00415FAE`.
- Diagnostic pointer cell `0x004213C8` resolves to `0x004317CC`:
  `lfs READ fail: block=%u, off=%u, size=%u, addr=0x%08X, st=%d`.

The callback uses the upstream five-argument littlefs read ABI: configuration
in `r0`, block in `r1`, offset in `r2`, buffer in `r3`, and size at the caller
stack slot. The configuration pointer is ignored.

## Recovered behavior

Address calculation is exactly
`0x01400000 + (block << 12) + offset` in 32-bit unsigned arithmetic. No local
block-count, offset, size, or overflow check is added; normal littlefs
configuration invariants remain the caller contract. The callback forwards
address, buffer, and size to the already source-owned guarded reader. A zero
driver result returns zero. Any nonzero result logs block, offset, size,
calculated address, and raw status, then returns `-5` (`LFS_ERR_IO`).

## Production evidence

Apple emits a 60-byte leaf at `0x00437FC4` (overlay offset 15,180), with
unrelocated SHA-256
`128ce01c51af09ed5433ccb3bfb1f097f54687a0ad38bbd33211d6af8d10ab5a`
and relocated SHA-256
`b1f49f83efac394d09db4885f1776717342630734fa0f9c2e25b984e626686db`.
Linux emits a 60-byte leaf at `0x00437FB4` (offset 15,164), with the same
unrelocated identity and relocated SHA-256
`6849e6a4a8eecdda8c35c324ba84da3a7a6a0d7adaf54ce4c18433d11ff426b9`.
Two strict relocations bind the source-owned reader and logger.

The canonical overlay is 15,240 bytes with SHA-256
`d68bca1fc09b1b734a65a706e9d5a4d5aa4201e53441f6ad1354be44f428b314`.
The 163,840-byte provider has SHA-256
`d98fa4fe7f8c01ebcc29219d7cd604a16eb702df85fbb04f1c15be9808c0cfdf`
and CRC-32C/MSB `0x36995A55`. It ends exactly at `0x00438000`. Exact
accounting is 15,225 source-owned, 16,396 generated patch, 16 alignment, and
132,203 retained official bytes across 198 functions, 179 relocated leaves,
and 196 patch sites.

The Apple unsigned package is 4,745,418 bytes with SHA-256
`41bb328e816ea68ad35b003ff63b3912a708bb72a987ec104047b79264b3a1e7`.
Its 4,562,636-byte flash plan has SHA-256
`f54d4336bb011546efce564defe697e9de93b820821759ac767fd6853de3feac`,
6,557 placed, two unresolved, five container-only, and six protected regions.
The Linux unsigned package is 4,521,412 bytes with SHA-256
`50fdf76b2bc0ced7be5a817962153281cdd5823e80d94a12fcc4b2368789d876`.

Five focused tests cover stock/successor identity, configuration and call
topology, successful forwarding, failure logging and mapping, stock wrap
behavior, and Cortex-M55 compilation. The aggregate closure gate passes 348
tests plus snapshot, routing, provider, analyzer, package, and flash-plan
checks.

## Physical block and next frontier

No signing, flashing, reset, boot, filesystem operation, or hardware access
was performed. No authorized responsive right G2 temple is available and the
left temple must remain stock. Live MSPI/NOR reads, partition contents,
filesystem reads, concurrency, diagnostics, and cold-boot evidence is
explicitly blocked by unavailable physical evidence.

The next executable entry is the program callback at `0x00421310`. Apple has
zero append headroom, so subsequent source closure must first authenticate and
implement reclaimed-body placement without crossing the protected main-image
boundary. Firmware-wide functional completeness is not claimed.
