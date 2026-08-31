# G2 bootloader automatic MSPI timing-selection source closure

> **Superseded temple-status premise:** Treat temple nonresponse/unavailability
> claims below only as history. The case was bumped during lunch and caused the
> disconnect, not firmware or flashing; exclude it from feasibility conclusions.
> Hardware testing remains blocked by unavailable physical evidence.

## Scope and evidence boundary

This closure covers authenticated bootloader bytes `[0x004201BA, 0x00420254)`
(154 bytes) from `blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin`.

- stock SHA-256: `a31a24975e2a7de11d5a42b05db91799e7e9656bca2cc22112867efdf9f2b9b7`
- retained caller: `0x004204BA`
- stock zero-fill seam: BL at `0x004201C4` to `0x00426C10`
- source-owned timing-scan seam: BL at `0x004201CA` to `0x00420002`
- retained diagnostic seam: BL at `0x00420210` and `0x0042024C` to `0x004176CE`
- active six-byte timing configuration: SRAM `0x2000023C`
- success/failure levels and lines: `2`/`0x1F3` and `1`/`0x1FB`

No target was attached, powered, flashed, erased, reset, booted, or otherwise
contacted while producing this closure.

## Recovered behavior

`open_cfw_bootloader_mspi_timing_auto_4201ba` reconstructs the complete bounded
entry:

1. Zero a six-byte local timing configuration.
2. Invoke the already source-owned exhaustive timing scan.
3. On scan success, copy exactly the six meaningful timing bytes into the
   active configuration at `0x2000023C` and emit the retained success record.
4. On scan failure, preserve the active configuration and emit the retained
   fallback record.

The authenticated compiler widened the success copy to eight bytes even though
the initialized and consumed timing object is six bytes. The reconstruction
deliberately copies only the six meaningful bytes so adjacent ABI padding or
state cannot be overwritten. The host fixture pins that safety property as well
as the success/failure branches, diagnostics, and sole timing-scan call.

## Reproducible source and artifacts

- source: `components/bootloader/core_overlay/runtime_mspi_timing_auto_4201ba.c`
- source size/SHA-256: 4,777 bytes / `60ef2a425997e8b4e760c0a2c2cf6cc139a336759ea1b400f9e2909cc798c8c8`
- Apple clang leaf: 172 bytes at overlay offset 11,064; unrelocated SHA-256 `c80f3e39201fd4dfb3648711af97e0f4eaa1e645c61d97f85bcab72bb3cfac8f`; relocated SHA-256 `96486cb54903f2e183aa7923a84f71f17027a24397e84dde3c9154a78d0b0e56`
- Homebrew LLVM leaf: 184 bytes at overlay offset 11,032; unrelocated SHA-256 `4fa315e0698a091384f055b8979788014ab41cf542c28048e8e1e2d31afda8b5`; relocated SHA-256 `93a5a7efa388f00b20ba1bf3d349614c932c4bf41436f9383878631ef570ede4`
- strict relocation: one `R_ARM_THM_CALL`, resolved by function identity to `open_cfw_bootloader_mspi_timing_scan_420002`

The authenticated entry is replaced by a generated Thumb-2 wide branch plus
NOP fill across all 154 bytes. The next unclosed bootloader frontier begins at
`0x00420254`.

## Deployment and validation boundary

The Apple provider is 159,836 bytes with SHA-256
`3fc36c66b22157230746e8b028ea84f2241b2d45e849aec4ae8e42f49ddef70e`;
the Linux provider is 159,816 bytes with SHA-256
`bc446214758b0cdde596d1fb171f86144d218a1a16755a41e9c79066fe3c0ea6`.
The corresponding complete unsigned packages are 4,741,414 and 4,517,404
bytes. Software evidence proves authenticated seams, host-observable state
publication/fallback behavior, strict cross-toolchain compilation and
relocation, deterministic provider assembly, package construction, and flash
planning.

Electrical timing-window quality, external-flash identification, XIP behavior,
and successful cold boot remain hardware-dependent. They cannot be validated
without an authorized responsive right G2 temple, so functional completeness is
not claimed.
