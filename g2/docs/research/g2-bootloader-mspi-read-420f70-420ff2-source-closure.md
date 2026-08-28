# G2 bootloader MX25U25643G guarded-read source closure

## Scope and authenticated boundary

This increment replaces the complete authenticated Apollo510B bootloader body
`[0x00420F70,0x00420FF2)` with clean-room compilable C. The stock body is 130
bytes with SHA-256
`ce201805b566c9d5c4a70d675e0bdb145133d2771bc9098e4255245a8d6067e3`.
The preceding six-byte gap `[0x00420F6A,0x00420F70)` has SHA-256
`86d14b79fc1438915684e8f5b80873e3458147a166ffdaa3a0d42aa9588c690f`;
the 214-byte successor pool `[0x00420FF2,0x004210C8)` has SHA-256
`21ac43cfda25ec0bc55b6df8e70c3341923392c939cf989b96f0945e7b151ba3`.
Both remain authenticated non-executable compatibility data. The direct
littlefs callback call is at `0x004212EE`.

## Recovered behavior

The entry accepts a 32-bit flash address, destination buffer, and length. A
null published handle at `0x200270DC`, null buffer, or zero length returns
status `6`; an address at or above `0x02000000` returns status `5`. Valid input
enters the source-owned transaction guard, selects source-owned quad mode, and
invokes the source-owned fixed ready wait. Stock ignores that wait result.

The entry then creates a zero-filled 24-byte Ambiq MSPI transfer descriptor:
length at offset `0`, address-present byte `1` at offset `7`, address at offset
`8`, instruction-present byte `1` at offset `12`, instruction `0x006C` at
offset `14`, direction byte `1` at offset `16`, and destination pointer at
offset `20`. It calls the retained blocking-transfer entry at `0x004262E0`
with timeout `1000000`, always releases the transaction guard afterward, and
returns the raw HAL status. `runtime_mspi_read_420f70.c` models those
observable contracts and contains no stock implementation bytes.

## Production routing and reproducibility

The stock entry is replaced by a wide Thumb branch plus NOP fill. Apple clang
emits a 152-byte leaf at overlay offset 14,440 / address `0x00437CE0`; its raw
SHA-256 is
`87dd2258a3f977fd79e3fde36da8d48b5aeea0568f3a9ae903d87844208360cb`
and its relocated SHA-256 is
`4acc213e830b898b6698c827bfd3e39e2f65d93844675047274315828a6cac71`.
Homebrew clang emits the same-size leaf at offset 14,416 / address
`0x00437CC8`, with the same raw SHA-256 and relocated SHA-256
`e59b5d745676d8911b1207f315f60e39aa352275ea805eb58894c9712479913a`.
Both profiles pin strict call relocations at offsets `40`, `44`, `48`, and
`94` to guard enter, quad-mode selection, fixed ready wait, and guard exit.

The canonical Apple/Linux overlays are 14,592 / 14,568 bytes with SHA-256
`b859abdddf191758b89dad26e6e4a4627da3cb4589db29d3da8dbf7d28ee82c6`
and `589400cae19f47b61b388952a4c08e37f51948905bc5d7a45c314ee0d46ff045`.
Providers are 163,192 / 163,168 bytes with SHA-256
`57b82aaa300029154900d1d817e565fd558a580fa6d76788cba2a8535379b37c`
and `0a46478d1d7a03959f0809334f2ee1416d94983805270d093bd82d79e2edb9ae`.
Provider accounting is 14,577 source-owned bytes, 15,812 generated redirect
bytes, 16 generated alignment bytes, and 132,787 retained official bytes.

Unsigned Apple/Linux packages are 4,744,770 / 4,520,756 bytes with SHA-256
`1d362e7f70d55b026361669a2b4c600a7b80c5b6a2e7570b0d386c7975e9d410`
and `8d4418b8a6e959d31ec10d5079a8ee5125950951555116029990c92ac405b0ac`.
The Apple flash plan is 4,556,102 bytes with SHA-256
`543047ab613f26906de128a6748f1ca860103e176f23eb226990313e205f7fe9`;
it records 6,548 placed, two unresolved, five container-only, and six
protected regions.

Five focused tests cover authenticated boundaries and the caller, all input
guards, exact call order and descriptor fields, ignored wait status, raw HAL
failure return with guard cleanup, and Cortex-M55 compilation. The complete
closure gate passes 327 tests plus all dependency snapshot, littlefs-port,
exact-routing, manifest, provider, analyzer, dual-package, and flash-plan
checks.

## Physical-evidence block

No signing, flashing, erase, reset, boot, pinmux mutation, MSPI command, or
other hardware operation occurred. There is no authorized responsive right G2
temple, and the left temple must remain stock. Consequently live handle state,
HAL descriptor acceptance and status behavior, wait timing, external-flash
read correctness, pinmux/electrical behavior, littlefs behavior, and cold-boot
qualification remain explicitly blocked by unavailable physical evidence.
This increment closes a software gap only and does not establish firmware-wide
functional completeness. The next authenticated executable frontier is
`0x004210C8`.
