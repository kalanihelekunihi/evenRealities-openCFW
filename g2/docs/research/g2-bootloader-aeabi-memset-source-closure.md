# G2 bootloader Arm EABI byte-fill source closure

Status: implemented in production source; physical boot validation blocked by unavailable authorized responsive hardware.

## Authenticated boundary

The G2 2.2.6.10 Apollo bootloader range `[0x0041560C,0x00415672)` is 102 bytes with SHA-256 `34da1a99d5cb56ca41cfaff98190ced2a7767f53cd95c53c504009566e9ca10a`. Its register contract is the Arm/IAR byte-fill convention: `r0` is the destination, `r1` the byte count, and the low byte of `r2` the fill value. A complete halfword-aligned scan finds exactly 20 direct Thumb `BL` callers at `0x00410538`, `0x00410E68`, `0x004110B6`, `0x004112D8`, `0x004116A8`, `0x00412488`, `0x00412950`, `0x00414548`, `0x004175D6`, `0x00417790`, `0x0041779E`, `0x0041783A`, `0x00417CDC`, `0x00417D46`, `0x00417DAC`, `0x0041CE62`, `0x0041FD7E`, `0x00422FC6`, `0x00426C1C`, and `0x0042DE66`. No strict-interior call or stored entry pointer is present.

## Production source and routing

`runtime_aeabi_memset.c` is a freestanding clean-room C loop with defined zero-count and low-byte semantics. Apple clang 21 and Homebrew clang 22.1.8 independently emit the same relocation-free 12-byte Thumb leaf, SHA-256 `57aa3a55299e81fefe7ae3b0807a149cf0d3d6c56adfcd6bf507f3850e6c229e`, at `0x00434824`. A generated non-linking `B.W` plus 49 Thumb NOPs replaces the complete authenticated stock span. Host tests cover zero length, every length through 64, byte truncation, and untouched suffix bytes.

The resulting canonical overlay is 952 bytes, SHA-256 `6b1d699a1484aa7952844de256ab0e1d8b13fae9dad31060a3cdcccb0e51b8cf`. The 149,552-byte provider hashes to `1ab985b3503145a6bd01aff07d6a283b362a2b9da9a4de745868bf9bbfb11d1f` and accounts for 947 compiled-source bytes, 1,050 generated patch bytes, six alignment bytes, and 147,549 retained official bytes. The Linux provider hash is `7cc3c8f9027fe2b999df3c580dd0b36ad5a01aeb8ca095ec54f9d4d976d99eff` at the same size.

The unsigned canonical package is 4,731,130 bytes with SHA-256 `ce547abd28cd269c34bf333b26be54c43f006ae1524463299b0a6f68e2c2dda8`; its 4,305,447-byte flash plan hashes to `68922229af4289af0b53910d7e942598781321a42ca2b66dc364dc41bbe53fe9` and records 6,201 placed, two unresolved, five container-only, and six protected regions. The LLVM 22.1.8 package is 4,507,140 bytes with SHA-256 `13f03c5c8d394e500dd8d448ecb01f3eb0714c7db3bf522e2dbcd447b5c82205`. These are local deterministic artifacts, not signed or flashed images.

## Validation boundary

`make bootloader-aeabi-memset-closure` rebuilds the full source package and then checks the host semantics, authenticated stock span, whole-image caller topology, strict leaf identity, placement, provider accounting, manifest ownership, and both deployment profiles. No tool in this closure signs, transmits, flashes, resets, or communicates with hardware.

Physical evidence requires an authorized responsive right temple with boot UART/debugger visibility demonstrating boot progression through the affected call paths. That device evidence is unavailable, so hardware validation remains explicitly blocked and firmware-wide functional completeness is not claimed.
