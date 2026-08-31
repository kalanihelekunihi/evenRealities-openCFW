# G2 bootloader MSPI device configuration source closure

## Result

The bootloader function at `[0x00424120, 0x0042488e)` is implemented by maintained, structured C and routed into production at its authenticated entry address. The implementation covers all 26 recovered device configurations and performs the recovered `DEV0CFG`, `DEV0XIP`, and `PADOUTEN` register transformations without raw instruction encodings.

This is software source closure, not hardware qualification. All-mode MSPI register, pad, XIP, clock-on-D4, and cold-boot qualification remains **blocked by unavailable physical evidence**.

## Production route

- Source: `components/bootloader/core_overlay/runtime_mspi_device_configure_424120.c`
- Interface: `components/bootloader/core_overlay/runtime_mspi_device_configure_424120.h`
- Runtime address: `0x00424120`
- Compiled body: 284 bytes
- Reviewed Apple and Linux body SHA-256: `960b3d30653a94dd8b0c9037d9e0cdd53991d88c06a9d27cecf6576a0bbce97f`
- Code relocations: 0
- License: BSD-3-Clause

The bootloader partition already ends at `0x00438000`, so an appended redirect leaf would overlap the Apollo application. The bounded implementation is therefore compiled in place over the authenticated first 284 bytes of the stock function. Both known callers continue to enter at `0x00424120`. The remaining stock bytes through `0x0042488e` are unreachable after the source-owned function returns; they remain explicitly accounted as retained official bytes alongside the independently live `mspi_piomixed_configure` successor.

## Authentication

- Stock function range: `[0x00424120, 0x0042488e)`
- Stock bytes: 1,902
- Stock SHA-256: `3b95c5af6c3c2140cc4e1522a1f284ae31825e4e35ae6c2427e0edba41774818`
- Known callers: `0x00425012`, `0x004258e4`
- Replaced stock prefix: 284 bytes
- Replaced-prefix SHA-256: `b47259eba440c6e177c86466f9b4606f10ff4eb85f12a3dbfb29b9303d0f37b6`
- Structured C SHA-256: `6ed08297ec6283b5ae48de7c2f1ab17c6ca8b2369e5f724ebed60f6fac18d262`
- Header SHA-256: `4842e22f3233f19e0edf383f1026726562b13cfaad14e42dfa2ccdb7296e313d`

The recovered ABI uses module offset 4, clock-on-D4 offset 9, and device-configuration offset 10. Module register bases are `0x40060000 + module * 0x1000`; the accessed offsets are `0x44`, `0x84`, and `0x90`.

## Verification

The host fixture exercises every one of the 26 configurations with clock-on-D4 disabled and enabled, checks read/write order and exact bit preservation, and confirms out-of-range modes are successful no-ops. The production analyzer additionally authenticates stock topology, upstream AmbiqSuite identity, source pins, both reviewed compiler identities, the 284-byte body digest, zero code relocations, production manifest routing, partition conservation, and absence of `.byte` or inline-assembly transcripts.

No hardware, MMIO, reset, signing, packaging, transmission, or flashing operation was performed.
