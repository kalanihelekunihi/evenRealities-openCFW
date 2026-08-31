# G2 bootloader MX25U25643G ready-poll source closure

> **Superseded temple-status premise:** Treat temple nonresponse/unavailability
> claims below only as history. The case was bumped during lunch and caused the
> disconnect, not firmware or flashing; exclude it from feasibility conclusions.
> Hardware testing remains blocked by unavailable physical evidence.

The complete authenticated polling cluster `[0x004207A2,0x00420800)` now
routes to maintained clean-room C. The 82-byte two-phase poll has SHA-256
`b5d741edee4dcb847a20256e315ae4304b07a43e02ef189da8c6a36ff0f9e809`;
the 12-byte fixed wrapper has SHA-256
`bceeab3a47379a62e78b6b07417c52a86da437468ee68ddb43e56468065e7329`.
Their shared 3,531-byte source SHA-256 is
`3818159361e949ac31c6c5e78c2f8236015ea2b76b571358efdd3fab789785b0`.

Stock disassembly and host evidence pin 200 initial status calls, a five-unit
delay after every unsuccessful initial call, and immediate success on a clear
status. The second phase performs at most the caller-supplied count: context
value 2 selects notification value 1, every other context selects a
1,000-unit delay, then status is checked. Exhaustion returns 1; any clear
status returns 0. The wrapper passes exactly 500. Retained/source-routed seams
are context query `0x00416088`, notification `0x00416378`, raw delay
`0x0041F9E6`, and busy status `0x0042074E`. Authenticated callers enter the
poll at `0x004207FA` and `0x00420B84`; eight callers enter the fixed wrapper.

Apple clang 21 emits relocation-free 88- and 12-byte leaves at offsets
12,576 and 12,664/runtime `0x00437598` and `0x004375F0`. Homebrew clang
22.1.8 emits relocation-free 88- and 12-byte leaves at offsets 12,560 and
12,648/runtime `0x00437588` and `0x004375E0`. The fixed wrapper leaf is
identical on both profiles; the poll leaf has reviewed profile-specific pins.
Apple/Linux overlay/provider identities are 12,676/161,276 bytes with SHA-256
`2d1a985fa932c1a5df7fb653c783a8867478eb13cd101ea0555d7dee72fd3d9a` /
`d130069cfea76cdc60e3205bd4d30cce52c3efb393d6655403dd9297a4eba729`
and 12,660/161,260 bytes with SHA-256
`1b07560689b47525b8696952a2c42f2a1b66fc8da22761335bb01c156a8d40e2` /
`27cbfb9e4a4761cf48697b5c1d2e1168ab7d7f64594a6abc7ec8d91fe0a4898d`.

Canonical accounting is 12,661 source-owned, 13,990 generated patch, 16
alignment, and 134,609 retained official bytes across 183 routed functions,
164 relocated leaves, and 181 patch sites. Unsigned Apple/Linux packages are
4,742,854 / 4,518,848 bytes with SHA-256
`68604c1267f678369cc4c4093882796b737e34f6d3b5493b386af832be96d4a9` /
`d21263e54b814263f69a992c5d37832d803354391f2e86979911dec015c39b2d`.
Their flash plans are 4,533,962 / 2,414,983 bytes with SHA-256
`330fa7c6a0818827b5d9c1b2d2701c35a1cb700481d1151cb6befd8c0db83a6c` /
`4aa530545d82768d64aed8144a4b1360325bd97b5565a4450d51047ea78fc1f5`;
they contain 6,517 / 3,459 placed regions and two unresolved hardware regions.

Nothing was signed, flashed, installed, reset, booted, or sent to hardware.
Live RTOS scheduling, delay units, status-register transitions, HAL/MSPI/XIP
behavior, and cold boot remain blocked by unavailable physical evidence from
an authorized responsive right G2 temple; the left temple must remain stock.
Executable bodies at and after `0x00420800` remain software gaps, so
firmware-wide functional completeness is not claimed.
