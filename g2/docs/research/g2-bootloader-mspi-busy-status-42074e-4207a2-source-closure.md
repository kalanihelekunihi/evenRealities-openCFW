# G2 bootloader MX25U25643G busy-status source closure

> **Superseded temple-status premise:** Treat temple nonresponse/unavailability
> claims below only as history. The case was bumped during lunch and caused the
> disconnect, not firmware or flashing; exclude it from feasibility conclusions.
> Hardware testing remains blocked by unavailable physical evidence.

The complete authenticated 84-byte entry `[0x0042074E,0x004207A2)` now
routes to `open_cfw_bootloader_mspi_busy_status_42074e` in maintained
clean-room C. The stock SHA-256 is
`33e47f7e0bf37502f2f2dd20196d15b67a1f3ef336cd48538ac99f6ceed0e6e5`;
the 3,114-byte source SHA-256 is
`361432557372303651f41bb8d3446d1f18f1753914fb8227fd6a4c57355685b8`.

Stock disassembly and host evidence pin a zeroed five-byte scratch object,
command `0x05`, no address phase, a one-byte read through the already
source-routed transfer entry at `0x004205F4`, and Boolean extraction of bit 7
from the returned status byte. A nonzero transfer status is returned unchanged
after the exact level-2 diagnostic using tag `0x00433CD8`, file
`0x00431540`, function `0x00433B00`, line 886, and format `0x00433508`.
The two authenticated callers are at `0x004207B6` and `0x004207E4`.

Apple clang 21 emits an 88-byte relocation-free leaf with SHA-256
`941545cc31870eadc0effa9a311c8e48788ffe3c33c644e58ccc11723ea304a5`
at offset 12,488/runtime `0x00437540`. Homebrew clang 22.1.8 emits an
88-byte relocation-free leaf with SHA-256
`118fc47e34df2fd63ff8ae3d7d7c335a7452b9520d224aa947e62c228360e378`
at offset 12,472/runtime `0x00437530`. Apple/Linux overlay/provider identities
are 12,576/161,176 bytes with SHA-256
`bcb06cd0183db6cbae2796ef0b221a95e90401963a7507094b0789763515422e` /
`8aaaf6add41db5ddeb010555c07acd867857dc15d629e8d06e6888e29f54297e`
and 12,560/161,160 bytes with SHA-256
`0cf8c6189d53dab0f905eaa3f4dbe86dc98e851e61da01faf93ea99aa3995044` /
`e5d0130641859309c318dae30f8e2ea191220cab04e382b612e6fd3ff88c783e`.

Canonical accounting is 12,561 source-owned, 13,896 generated patch, 16
alignment, and 134,703 retained official bytes across 181 routed functions,
162 relocated leaves, and 179 patch sites. Unsigned Apple/Linux packages are
4,742,754 / 4,518,748 bytes with SHA-256
`16f3b3f7d04f4b8cf4668b62032605fb95c988ec357b74ae9c5a4d9270615648` /
`22b42679b0c58a345bbce3962d0e1153977bf570f03a9b69bfcfb3f31b649325`.
Their flash plans are 4,531,098 / 2,413,481 bytes with SHA-256
`d3c2789230b3be293a1baa1493da599cc09d1e9d98c831cb16d7e84e487455e9` /
`4c5059453de378c9cdb4db516790707cc51f66b44497b72e8f22db45ef590d13`;
they contain 6,513 / 3,457 placed regions and two unresolved hardware regions.

Nothing was signed, flashed, installed, reset, booted, or sent to hardware.
Live status-register semantics, HAL/RTOS timing, external-flash/MSPI/XIP
behavior, and cold boot remain blocked by unavailable physical evidence from
an authorized responsive right G2 temple; the left temple must remain stock.
The next executable body `[0x004207A2,0x004207F4)` remains a software gap, so
firmware-wide functional completeness is not claimed.
