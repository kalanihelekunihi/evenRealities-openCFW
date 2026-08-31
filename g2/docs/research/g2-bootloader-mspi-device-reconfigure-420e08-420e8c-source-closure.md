# G2 bootloader MSPI device-reconfiguration source closure

> **Superseded temple-status premise:** Treat temple nonresponse/unavailability
> claims below only as history. The case was bumped during lunch and caused the
> disconnect, not firmware or flashing; exclude it from feasibility conclusions.
> Hardware testing remains blocked by unavailable physical evidence.

## Result

The complete authenticated 132-byte entry `[0x00420E08,0x00420E8C)` now
routes to maintained clean-room C in
`components/bootloader/core_overlay/runtime_mspi_device_reconfigure_420e08.c`.
The stock body SHA-256 is
`575026ee48ade40393f0bf4f6bcaaf005966b05d97246e9170ae8201f15ec61c`;
the 5,594-byte source SHA-256 is
`23ce33f81eacea40350c99427d0156e488b2d28d80a7bb040438fe55f91c2551`.
Its two direct callers are `0x00420EB4` and `0x00420F14`. The next executable
entry begins immediately at `0x00420E8C`.

## Authenticated behavior

The entry reads the MSPI handle from `0x200270DC`, disables the controller at
`0x004250F0`, applies the caller's device configuration through
`0x00424BE4`, and re-enables the controller through `0x00425066`. Any nonzero
HAL result emits the exact EasyLogger diagnostic and returns `1`; the raw HAL
status is deliberately collapsed. Disable uses line `0x58A` and format
`0x00432E08`. Configure and enable use lines `0x592` and `0x59A` and format
`0x00432E2C`.

On success, the entry reads the initialized state pointer from `0x200270D8`,
loads its first word as the MSPI instance, reads the device selector byte at
configuration offset `+8`, and calls the separately source-owned pin-group
dispatcher at `0x0041FADC`. It then returns zero. The implementation preserves
the stock assumption that the configuration and published state pointers are
valid; it does not invent null-pointer policy.

Host tests prove the exact success order, handle and configuration propagation,
state-instance and device-byte selection, all three failure short circuits,
collapsed return status, exact diagnostics, stock body/calls/callers/literals,
and Cortex-M55 compilation.

## Build and deployment evidence

Apple Clang emits a 136-byte leaf at overlay offset 14,028/runtime
`0x00437B44`, with raw/final SHA-256
`065da9327ea493b21dc7d44cc863947c88a5d1c407f031ed1d9327e320ef8204` /
`7be99b6cd10ca4a8bcb4dc893a246c439a117d95798ab566d9f5def8d35d60f4`.
Linux Clang emits a 128-byte leaf at offset 14,012/runtime `0x00437B34`, with
raw/final SHA-256
`24370abff2d456f5b1c092d75735b08d02e35efb3667a5a16a755852f4c6e006` /
`cb64980a695ec004729d21b3801f8228b3d59672c835147c681d7bbab482910f`.
Each has one strict `R_ARM_THM_CALL` relocation to the source-owned pin-group
dispatcher, at leaf offsets 98 and 90 respectively.

Apple/Linux overlay identities are 14,164 /
`afd9bcfa294f66ffb92c17c5d562a7c8e1cb6d95c6bf49ebd00cb8d315e26e5a`
and 14,140 /
`cda5772f628c68390b477329eea3ccba4e4138aa0d53f1dd3485ef3086a27881`.
Provider identities are 162,764 /
`dc3e8e2fecad73b3db6550353ea12317b7a5a5fe2b1a0415871f8a510d0185b5`
and 162,740 /
`3a40fd8e34da6c07eef37c1018323db537a8f8ef3bbdd062637637ca6ceba155`.
Canonical provider accounting is 14,149 source-owned, 15,464 generated patch,
16 alignment, and 133,135 retained official bytes across 191 functions, 172
relocated leaves, and 189 patch sites.

Unsigned Apple/Linux packages are 4,744,342 /
`fd48ce7f025a78835fe08478da55b5146c359ca3ac050e092a98366c2c212a81`
and 4,520,328 /
`d02f9da0600b62b85c3867cd542ce769b8d72cbe1d15ccbb98b103ad5891c6a8`.
Their flash plans contain 6,540 / 3,474 placed regions and two unresolved
physical regions. The Apple flash plan is 4,550,391 bytes with SHA-256
`8f614af21940ad4b865078d0c00334adfd0201faea3d4ed1c8e35bd17ab16188`;
the Linux plan is 2,425,912 bytes with SHA-256
`a728de2f061618b093deee8db4dbc7dd147bdfeaacdd660999224d6748bb15be`.

## Physical-evidence boundary

Nothing was signed, flashed, installed, reset, booted, or sent to hardware.
Live HAL disable/configure/enable, pinmux, MSPI, external-flash, XIP, timing,
and cold-boot behavior cannot be validated because no authorized responsive
right G2 temple is available; the left temple must remain stock. The next
executable entry at `0x00420E8C` remains a software gap, so firmware-wide
functional completeness is not claimed.
