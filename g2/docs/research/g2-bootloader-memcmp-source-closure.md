# G2 bootloader bounded byte-comparison source closure

> **Superseded temple-status premise:** Treat temple nonresponse/unavailability
> claims below only as history. The case was bumped during lunch and caused the
> disconnect, not firmware or flashing; exclude it from feasibility conclusions.
> Hardware testing remains blocked by unavailable physical evidence.

Status: implemented in production source; physical boot validation blocked by unavailable authorized responsive hardware.

The authenticated bootloader range `[0x00415758,0x004157C0)` is 104 bytes with SHA-256 `33e09969a8e4f7ca9290ef4678d252c217a5d031eb362f8d6c5ad656424d4154`. It implements the standard three-argument bounded byte-comparison contract and has exactly six direct Thumb callers at `0x00410738`, `0x00411D0A`, `0x00411D1E`, `0x00411D42`, `0x00411D54`, and `0x0042DA9A`; no strict-interior or stored-pointer ingress is present.

`runtime_memcmp.c` is a clean-room freestanding C implementation. It returns zero for equal prefixes and a value with the unsigned first-difference sign otherwise. Apple clang 21 and Homebrew clang 22.1.8 emit the same relocation-free 28-byte Thumb leaf, SHA-256 `27a66a6c870f14f8ff02ed06584fc60e5e6bb17274f13e4234314e5fcbb2ece1`, at `0x00434840`. A non-linking `B.W` plus 50 NOPs replaces the complete stock span. Host tests cover count zero, all equal counts through 64, first differences at both aligned and unaligned positions, sign symmetry, prefix exclusion, and unaligned equal inputs.

The canonical overlay is 996 bytes, SHA-256 `474ab9cc0002c329d2d6eb3461e10766fb08fbd65a8fb7e25965056388210ae5`. The 149,596-byte provider hashes to `89544a6cb9e05f191aeb5ee7bfd9ade178dd4a9669e502432c77fb891ec50d01` and accounts for 991 compiled-source bytes, 1,320 generated patch bytes, six alignment bytes, and 147,279 retained official bytes. The Linux provider hash is `6bedcd06aff5cb5e9aa8e051d717e7385c29449ef5572a36cda57c6206227604`.

The unsigned canonical package is 4,731,174 bytes with SHA-256 `93fc5881fc8171a0094100bc5075f904aea10e9f6176f06f8d3c70b6fff5eb80`; its 4,309,608-byte flash plan hashes to `cbb8c1349d62e0d4846d05112dd782080bafb3923a0706181d261de208e3d644` with 6,207 placed, two unresolved, five container-only, and six protected regions. The LLVM package is 4,507,184 bytes with SHA-256 `1c5571bb3bb6072f5d91f883c07fd8fddc486fca9ef6a5f4624a810a58192e89`. They are deterministic local artifacts and were not signed, transmitted, or flashed.

`make bootloader-memcmp-closure` rebuilds the full source package and checks source/stock identities, host semantics, all callers, leaf placement, provider accounting, manifest ownership, and both compiler profiles. Physical acceptance still requires an authorized responsive right temple with boot UART/debugger visibility. That evidence is unavailable, so hardware validation is explicitly blocked and firmware-wide completeness is not claimed.
