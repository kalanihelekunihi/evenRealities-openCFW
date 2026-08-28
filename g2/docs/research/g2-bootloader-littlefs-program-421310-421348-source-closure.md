# G2 bootloader LittleFS program callback source closure

The complete authenticated callback `[0x00421310,0x00421348)` is implemented
as freestanding C and production-routed to a fixed-address source leaf in
authenticated reclaimed body space. This is software closure only; no device
was contacted, and live flash programming remains blocked by unavailable
authorized responsive right-temple hardware.

## Authenticated stock evidence

- Program callback: 56 bytes, SHA-256
  `6d46e88d2df85850b8ec35b4f55e5e0522884210c8bf5a3419e328599ffebf60`.
- Successor erase callback `[0x00421348,0x00421372)`: 42 bytes, SHA-256
  `df1788d1db60223b7af5050ab14307a3bf27f30fc6d61917adee77f679b3b872`.
- The LittleFS configuration program pointer at `0x00431078` is
  `0x00421311`.
- The callback calls the source-owned program driver entry formerly at
  `0x00420B0C`, logs through the source-owned dispatcher, and uses the
  authenticated diagnostic format addressed by the literal at `0x004213CC`.

The recovered five-argument ABI ignores `cfg`, calculates
`0x01400000 + (block << 12) + offset` with 32-bit wrap, forwards
`(address, buffer, size)`, returns zero on success, and logs the complete
block/offset/size/address/status tuple before mapping every nonzero device
status to LittleFS `LFS_ERR_IO` (`-5`).

## Source and fixed-address cave

`runtime_littlefs_program_421310.c` is 1,655 bytes with SHA-256
`549c41f98a30bc4f3abdbb0fcd1c94dfd16629349fe7c0974a1f87eff5106ea4`.
Both reviewed toolchains emit a 60-byte leaf with identical unrelocated
SHA-256 `0c3f616821d792fe1cff00d305ea8c817564ced4ed73bd655a3492b78728ae42`.
The relocated Apple leaf SHA-256 is
`38ee6601a1b224a6aaac64f7700a491632e765e083aa40c80445b2cedcb81c7f`;
the Linux leaf SHA-256 is
`6492e96d244e39380674e979ae1b0e3eebef00220ee3343f14c8683113fa4e78`.

Apple append space is exhausted, so the leaf is fixed at
`[0x00421214,0x00421250)`, inside the NOP tail generated after the authenticated
initializer redirect at `0x00421210`. The builder first authenticates and
replaces every original stock span, then requires the cave to be word-aligned,
non-overlapping, wholly inside exactly one generated entry-replacement tail,
byte-for-byte NOP fill, and SHA-256
`63fd82bc7c6b56fa45121d1605db9aeac6928cdb9123b347db41b8a8e56f4de0`.
Only then does it install the fixed-address leaf. Negative tests reject an
out-of-tail address and a forged generated-NOP digest.

## Production artifacts

- Apple bootloader provider: 163,840 bytes, SHA-256
  `ef42f8f927e07a2962e4a9c9436c6cf4df24dc6cf5206f09823f5ad42afba410`,
  CRC-32C/MSB `0x0CE766B1`; ends exactly at `0x00438000`.
- Linux bootloader provider: 163,824 bytes, SHA-256
  `2d09f6ba1ed39fc2f7bf3c658d2ef884c2596d6d666455b22fba1b9638ee0004`.
- Apple unsigned package: 4,745,418 bytes, SHA-256
  `ca6c0ac3fb5c1c7c4ef7b83cc184d671133a671cd9027310e3214e1fba2312c0`.
- Canonical flash plan: 4,564,800 bytes, SHA-256
  `29dcb55776458fcd0a181850afba054754a3618242ca9052ce7bb22505837736`,
  with 6,560 placed, two unresolved, five container-only, and six protected
  regions.
- Linux unsigned package: 4,521,412 bytes, SHA-256
  `0298e63de18eaaac5874c27da786fe3113e090d2e52550f253f1930156fba901`.

Apple provider accounting is 15,285 source-owned bytes, 16,392 generated
patch-site bytes, 16 generated alignment bytes, and 132,147 retained official
bytes. The next retained executable entry is the erase callback at
`0x00421348`.

## Qualification boundary

Host behavior, dual-toolchain compilation, relocation, fixed-address cave
placement, provider layout, manifest integration, package assembly, and flash
plan generation are offline-validated. No signing, flashing, installing,
erasing, resetting, booting, or target communication occurred. Real MSPI NOR
programming, LittleFS write persistence, reboot recovery, and error telemetry
remain explicitly hardware-validation blocked.
