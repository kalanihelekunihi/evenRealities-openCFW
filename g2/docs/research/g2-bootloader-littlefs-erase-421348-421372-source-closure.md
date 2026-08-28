# G2 bootloader LittleFS erase callback source closure

The authenticated callback `[0x00421348,0x00421372)` is implemented as
freestanding C and production-routed to a second fixed-address leaf in
authenticated reclaimed initializer body space. This is offline software
closure only; live erase remains blocked by unavailable authorized responsive
right-temple hardware.

## Evidence and behavior

- Stock body: 42 bytes, SHA-256
  `df1788d1db60223b7af5050ab14307a3bf27f30fc6d61917adee77f679b3b872`.
- Successor literal/gap `[0x00421372,0x004213D4)`: 98 bytes, SHA-256
  `69c23d9c23df577cb63407fd0899c61afc102f15fc1a38f710fde8d829b71d2b`.
- Configuration erase pointer at `0x0043107C`: `0x00421349`.
- Direct source-owned seams: sector erase formerly at `0x00420A08` and the
  logger formerly at `0x00415FAE`; the diagnostic format address is
  `0x00432568`.

The callback ignores `cfg`, calculates `0x01400000 + (block << 12)` with
32-bit wrap, forwards the address, returns zero on success, and logs
block/address/status before mapping every nonzero status to `LFS_ERR_IO`
(`-5`).

## Cave and artifacts

`runtime_littlefs_erase_421348.c` is 1,302 bytes with SHA-256
`4d58acad65ca7fa61dc8c1594c84da01d08341eaf1a7d2a592d0ba2b073ab3da`.
Apple/Linux emit 48-byte leaves at `[0x00421250,0x00421280)` with unrelocated
SHA-256 `a937afb24c1164ec483d9f7ed5188558207f9ac9693c95fe37af7f0adbf84832`.
Relocated SHA-256 values are
`a7596457005b6c6df89c5e8515abf8c5458401d9c50b1e0a09e63ddcbce1c47a`
and `70908e6d968fbb31844e97596e76ca46e5ec2035107ebd6c1b687029677c8b11`.
The authenticated generated-NOP digest is
`88eaa9b4ef65616cd837de01f4973fd42d71bb31eb876a1a89aa67616f18fbdb`.

Apple/Linux providers are 163,840 /
`a4a1ff23a237f05a514a73c17d068c2fc27e6eb3f06c9a030387d277c0cde99f`
and 163,824 /
`528ea3ce26d7acdf93a79be2b3cfde38663b13f85ae1a37028a85fc27ddbde84`.
Apple CRC-32C/MSB is `0x0DF4D6FD`. Canonical accounting is 15,333
source-owned, 16,386 generated patch, 16 alignment, and 132,105 retained
official bytes.

Apple/Linux unsigned package SHA-256 values are
`7b260362c3e5c2f3e9bb249a6a5dace696518a25bb2e65c8b2a2898dd9e471f5`
and `718e66428467cbc01a225e118e047b323d160271809b37e20872208933f0b235`.
The 4,566,262-byte canonical flash plan has SHA-256
`703ac616c132c39f9d2670a9a376e32a6558653c5d475bb203c53eb5ffb63c82`
with 6,562 placed, two unresolved, five container-only, and six protected
regions.

No signing, flashing, erase, reset, boot, or device communication occurred.
Live NOR erase, LittleFS allocation behavior, persistence, power-loss, and
diagnostics remain explicitly hardware-validation blocked. The next retained
executable entry is the sync callback at `0x004213D4`.
