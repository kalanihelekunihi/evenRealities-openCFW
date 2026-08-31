# G2 bootloader MSPI timing-scan source closure

> **Superseded temple-status premise:** Treat temple nonresponse/unavailability
> claims below only as history. The case was bumped during lunch and caused the
> disconnect, not firmware or flashing; exclude it from feasibility conclusions.
> Hardware testing remains blocked by unavailable physical evidence.

## Scope and evidence boundary

This closure covers authenticated bootloader bytes `[0x00420002, 0x004201BA)` (440 bytes) from `blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin`.

- stock SHA-256: `9618b6beec8ecb55dc3e00510fb11d23951d2c145521c3b418bc445451d6dcb6`
- retained caller: `0x004201CA`
- retained MSPI control seam: BL at `0x00420036` to `0x004251C0`
- retained JEDEC-ID read seam: BL at `0x0042003C` to `0x0042059E`
- source-owned helper seams: BL at `0x004200BE` to `0x0041FF60`, and BL at `0x00420158` to `0x0041FF74`
- expected packed JEDEC ID: `0x002539C2`
- 36-by-6 timing table: SRAM `0x20000244`

No target was attached, powered, flashed, erased, reset, booted, or otherwise contacted while producing this closure.

## Recovered behavior

`open_cfw_bootloader_mspi_timing_scan_420002` reconstructs the complete bounded entry:

1. Clear 36 pass masks and a six-byte working configuration.
2. For each of the 36 timing-table rows, copy the four coarse fields, force turnaround byte 5 to 8, and test every fine delay from 0 through 31 in byte 4.
3. Submit MSPI control request 16 and read the device identifier for every candidate. Mark a fine delay as passing only when the read returns status zero and ID `0x002539C2`.
4. Use the source-owned longest-run helper on every row, retaining the first row whose run is strictly longer than the prior best.
5. Emit the three retained diagnostic records, compute the winning run center through the source-owned center helper, and return the selected six-byte table row with byte 4 replaced by that center.
6. Return zero, matching the authenticated entry contract.

The host fixture executes all 1,152 scan candidates, verifies first-longest tie behavior, output construction, diagnostics, and the all-failed edge case.

## Reproducible source and artifacts

- source: `components/bootloader/core_overlay/runtime_mspi_timing_scan_420002.c`
- source size/SHA-256: 9,485 bytes / `bbf4ccc39eff32fbf45ef5a880f78eb6fec934394ea888f47140ca7b0c0d4c50`
- Apple clang leaf: 420 bytes at overlay offset 10,644; unrelocated SHA-256 `b3582162aa1a50ecf33e55f380293a100a5fde5d9db41043f8f796b268c0ccb2`; relocated SHA-256 `184a82c6cb821121c638e1b237802adc07ffa89d7c9655262156e4c8c32ce481`
- Homebrew LLVM leaf: 420 bytes at overlay offset 10,612; unrelocated SHA-256 `9ad7c20e93d62367fcb73fdb9ba210cc1c204423518ca9a7b3999ca3a4ae8daa`; relocated SHA-256 `794f106a21e1407b06403e93593f5df8a9ed74c426b31f50cd2e7f30e204c733`
- strict relocations: two `R_ARM_THM_CALL` records, each resolved by function identity to the already source-owned bit-run helpers

The authenticated entry is replaced by a generated Thumb-2 wide branch plus NOP fill across all 440 bytes. The next unclosed bootloader frontier is the timing-auto caller at `0x004201BA`.

## Validation boundary

Software evidence proves authenticated seams, host-observable algorithm behavior, strict cross-toolchain compilation/relocation, deterministic overlay placement, and provider generation. Electrical timing-window quality and successful identification of the physical flash remain hardware-dependent and cannot be validated without an authorized responsive right G2 temple.
