# G2 bootloader MX25U25643G serial-mode source closure

> **Superseded temple-status premise:** Treat temple nonresponse/unavailability
> claims below only as history. The case was bumped during lunch and caused the
> disconnect, not firmware or flashing; exclude it from feasibility conclusions.
> Hardware testing remains blocked by unavailable physical evidence.

## Scope and authenticated boundary

This increment replaces the complete authenticated Apollo510B bootloader body
`[0x00420F10,0x00420F6A)` with clean-room compilable C. The stock body is 90
bytes with SHA-256
`b73005fad7b0cae8e2f2273bae21ab2877963d2d14534b5afc2918c515c26a13`.
Its four direct callers are `0x004204B6`, `0x004204BE`, `0x00420A4C`, and
`0x00420B58`. The six bytes at `[0x00420F6A,0x00420F70)` are authenticated
successor gap/literal data and are not claimed as executable source.

## Recovered behavior

The entry passes the initialized-SRAM serial configuration at `0x2000020C` to
the source-owned MSPI device-reconfiguration service. A nonzero result emits
the stock failure record and returns. Success calls the source-owned XIP
configuration service with mode `0`, then issues retained Ambiq HAL control
request `0x18` through the handle at `0x200270DC` with a zero mode byte. A
control failure emits the stock line-`0x5C7` record; the reconfiguration
failure uses line `0x5C0`. Both preserve the authenticated logger tag at
`0x00433CD8`, file identity at `0x00431540`, and format-string identities at
`0x00432E74` and `0x00433260`. The function returns no status.

`runtime_mspi_set_serial_mode_420f10.c` models those observable contracts. It
uses explicit seams for source-owned reconfiguration and XIP policy and for
the retained logger and HAL control calls; it contains no stock implementation
bytes.

## Production routing and reproducibility

The stock entry is replaced by a wide Thumb branch plus NOP fill. Apple clang
emits a 124-byte leaf at overlay offset 14,316 / address `0x00437C64`; its raw
SHA-256 is
`4af379ff55bf842dcfd2cc6589a6e4c0c27012bd9cbbf74d6baee92a9e51736b`
and its relocated SHA-256 is
`7bd7debf9e5a4c3eea789c950410381f3579bf14a97f92ccc45d453457949ba9`.
Homebrew clang emits a 124-byte leaf at offset 14,292 / address `0x00437C4C`;
its raw SHA-256 is
`af0e741e2bf02ba83fbec8568fbb67902c0cff155fe5e740f3d1b5c6bd71e270`
and its relocated SHA-256 is
`420057be3b9a6f5aaf0261f4078c6ed66eb38c208b4e0f864da6d3725c11fcb3`.
Each profile has strict calls at leaf offsets `4` and `40` to device
reconfiguration and XIP configuration respectively.

The canonical Apple/Linux overlays are 14,440 / 14,416 bytes with SHA-256
`b238c479b5e41d1fccc07b42328636fb4cfa570b660bc44d919c6e6dda8988d2`
and `e9db16d933b638422b1b798dbe9619c543d63622afe2acd5dbd61c89699b10de`.
Providers are 163,040 / 163,016 bytes with SHA-256
`9afda4d9585fa153fdb38f6539069aa48e74100a20f015e72c883d7416318fae`
and `a364ae072e1f76cfe71a7a5fc64bab1aa7732797cf4d29195f942d9f50d8d3ca`.
Provider accounting is 14,425 source-owned bytes, 15,682 generated redirect
bytes, 16 generated alignment bytes, and 132,917 retained official bytes.

Unsigned Apple/Linux packages are 4,744,618 / 4,520,604 bytes with SHA-256
`e436759ab14c5a967632d4c993a4313c28b00f384a4e78f54cac5e804ca5dad9`
and `fa956f608b507d2429414d7cebd45f77f678953db8b3916a5975cc3e31196657`.
The Apple flash plan is 4,554,031 bytes with SHA-256
`e78f9e19debe8e99202faf251eb278dd90f695d53973ff165d1933fd3163f07d`;
it records 6,545 placed, two unresolved, five container-only, and six
protected regions.

Five focused tests cover the authenticated boundary, callers and successor
gap, successful call order and arguments, both failure paths, exact logging,
and Cortex-M55 compilation. The complete closure gate passes 322 tests plus
all dependency snapshot, exact-routing, manifest, provider, analyzer,
dual-package, and flash-plan checks.

## Physical-evidence block

No signing, flashing, erase, reset, boot, pinmux mutation, MSPI command, or
other hardware operation occurred. There is no authorized responsive right G2
temple, and the left temple must remain stock. Consequently initialized-SRAM
template validity, live HAL return behavior, XIP transitions, external-flash
mode behavior, pinmux/electrical behavior, and cold-boot qualification remain
explicitly blocked by unavailable physical evidence. This increment closes a
software gap only and does not establish firmware-wide functional
completeness. The next authenticated executable frontier is `0x00420F70`.
