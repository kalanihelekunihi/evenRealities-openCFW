# G2 bootloader MSPI PIO-mixed configuration source closure

## Result

The bootloader function at `[0x0042488e, 0x00424976)` is implemented by maintained structured C and routed in place at its authenticated entry. It maps all 26 recovered PIO configurations to the low nibble of the per-module PIO register and preserves every unrelated register bit. The public production source contains no raw instruction encoding or inline assembly.

This is software source closure, not hardware qualification. Live PIO mode, pad, XIP, module, and cold-boot qualification remains **blocked by unavailable physical evidence**.

## Production identity

- Source: `components/bootloader/core_overlay/runtime_mspi_piomixed_configure_42488e.c`
- Interface: `components/bootloader/core_overlay/runtime_mspi_piomixed_configure_42488e.h`
- Runtime address: `0x0042488e`
- Compiled body: 84 bytes
- Apple/Linux SHA-256: `6269fba16f490f502f6d00c87e76b4fa9521b9d9e97fbf6f7a04dd02ec9f6044`
- Code relocations: 0
- Section alignment: 2 bytes, emitted with `-mpure-code` so no address literal forces 4-byte placement
- License: BSD-3-Clause

The fixed bootloader partition has no append headroom. The 84-byte body therefore replaces the authenticated stock prefix directly. The source function returns before the remaining 148 stock bytes, which stay explicitly classified as an unreachable retained tail. The independently source-owned dummy and sequence-loopback successors remain at `0x00424976` and `0x00424978`.

## Authentication

- Complete stock body: 232 bytes
- Complete stock SHA-256: `e8323e8e0ac6f59465ce1d30087eb6f4a2e3de336c45bff3e6954325a2e32fee`
- Caller: `0x004258b8`
- Replaced stock prefix: 84 bytes
- Replaced-prefix SHA-256: `32c77f9450e13e82e09fd35d65f8f6d3271cf9b15b32fa29cccff5f87b24fa39`
- Source: 1,939 bytes / SHA-256 `90f8f61f648b6086e14faf7a2fdfe68e1c11615bc4df1d4ea4c113c46e6b4f29`
- Header: 1,401 bytes / SHA-256 `2f97f272af211bb37a4d73e7f9d4373f209364eafccb868a4af83b669cf0c677`

The recovered ABI uses module offset 4 and PIO-configuration offset 11. The target register address is `0x40060004 + module * 0x1000`.

## Verification

The host fixture covers every supported mode, exact read/write counts and address, low-nibble replacement, unrelated-bit preservation, and out-of-range no-op behavior. The production analyzer also authenticates stock topology, both reviewed compiler identities, zero relocations, all three adjacent source routes, manifest partitioning, byte conservation, and the source-quality gate.

No hardware, MMIO, reset, signing, transmission, or flashing operation was performed.
