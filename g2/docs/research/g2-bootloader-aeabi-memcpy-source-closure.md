# G2 bootloader Arm EABI forward-copy source closure

> **Superseded temple-status premise:** Treat temple nonresponse/unavailability
> claims below only as history. The case was bumped during lunch and caused the
> disconnect, not firmware or flashing; exclude it from feasibility conclusions.
> Hardware testing remains blocked by unavailable physical evidence.

Status: implemented in production source; physical boot validation blocked by unavailable authorized responsive hardware.

## 2026-09-01 dual-entry correction

The span also has a live aligned entry at `0x004156AC` with 29 direct callers.
The earlier single-entry premise and whole-span NOP fill were incomplete. The
overlay now uses independent redirects at `0x0041568C` and `0x004156AC`, both
targeting the same source implementation. See
`g2-bootloader-aeabi-memcpy-dual-entry-routing-correction.md`. Current physical
boot validation remains **blocked by unavailable physical evidence**.

## Authenticated boundary

The G2 2.2.6.10 Apollo bootloader range `[0x0041568C,0x00415732)` is a 166-byte optimized forward-copy routine with SHA-256 `8e696e1fb54917a436f850e562f74e8cc8734c259fdaac9f767a3c264ff427cd`. Its register contract is the Arm EABI convention: `r0` is the destination, `r1` the source, and `r2` the byte count. It copies in increasing address order, handles unaligned endpoints, does nothing at count zero, and provides no overlap guarantee. A complete halfword-aligned image scan pins 33 direct Thumb `BL` callers to the general entry and 29 to the aligned entry; it finds no other direct ingress or stored entry pointer in the span.

## Production source and routing

`runtime_aeabi_memcpy.c` is a freestanding clean-room C loop. Apple clang 21 and Homebrew clang 22.1.8 independently emit the same relocation-free 16-byte Thumb leaf, SHA-256 `d2d832a0c13fc4c0b9b47396bfb6d68fb7e07925ad0fa4eedc9c14c5b062590d`, at `0x00434830`. Generated non-linking `B.W` redirects at both live entries plus bounded Thumb NOP fills replace the complete stock span. Host tests cover every count through 64 and aligned/unaligned source/destination combinations while checking both untouched prefixes and suffixes.

The resulting canonical overlay is 968 bytes, SHA-256 `dc98b257789403636430c9c98e46fbeddaa8813429e6940b3f9a9b4519d14e23`. The 149,568-byte provider hashes to `acd78e607babaf5abc92bbd98ceda845cd44d625038816b8a6919a9d35a16d25` and accounts for 963 compiled-source bytes, 1,216 generated patch bytes, six alignment bytes, and 147,383 retained official bytes. The Linux provider hash is `a72290ddf75caffac18c6bd23673227454f5df4bfa711a271c1c779ed3e54da5` at the same size.

The unsigned canonical package is 4,731,146 bytes with SHA-256 `9454c8dde4e582243b8253a2ea3b9524982f80574a3231204d101c1b1f3c5c4b`; its 4,307,542-byte flash plan hashes to `920a9e29debf48de1bf1d2fb4c33c29f7ed108f553d0f916f629178bf5228d1d` and records 6,204 placed, two unresolved, five container-only, and six protected regions. The LLVM 22.1.8 package is 4,507,156 bytes with SHA-256 `b456536e1c92f9d9275cfd13d4225d5cdb3c0fc42f892340a7bc7edb80740974`. These are local deterministic artifacts, not signed or flashed images.

## Validation boundary

`make bootloader-aeabi-memcpy-closure` rebuilds the source package and then checks host semantics, the authenticated stock span, all 62 callers across both entries, strict leaf identity, placement, provider accounting, manifest ownership, and both deployment profiles. No closure tool signs, transmits, flashes, resets, or communicates with hardware.

Physical evidence requires an authorized responsive right temple with boot UART/debugger visibility demonstrating boot progression through the affected call paths. That evidence is unavailable, so hardware validation remains explicitly blocked and firmware-wide functional completeness is not claimed.
