# G2 bootloader substring-search source closure

> **Superseded temple-status premise:** Treat temple nonresponse/unavailability
> claims below only as history. The case was bumped during lunch and caused the
> disconnect, not firmware or flashing; exclude it from feasibility conclusions.
> Hardware testing remains blocked by unavailable physical evidence.

Status: software implemented and production-routed; physical validation blocked.

The aggregate identities below are the substring promotion checkpoint; the
later critical-context promotion supersedes them. Current aggregate pins are
in `g2-bootloader-critical-context-source-closure.md`.

The complete stock entry `[0x00415FFA,0x00416026)` is 44 bytes with SHA-256
`b3d23ab7bd57fe606d7b10914614adcf04fdb10bca25899ee7cd301d38f3ae40`.
It implements standard `strstr` semantics: an empty needle returns the input
haystack; otherwise it locates successive first-character candidates and
returns the first complete match or null. Six whole-image Thumb call sites are
pinned at `0x004153C6`, `0x004153D6`, `0x004153E8`, `0x004153FA`,
`0x0041776E`, and `0x00417A86`. The final two are EasyLogger tag and keyword
filters. The preceding `[0x00415FDA,0x00415FFA)` bytes are logging literal
data; the following two-byte infinite-loop and return stubs are distinct
boundaries and are not absorbed by this closure.

`runtime_strstr.c` is a 628-byte MIT clean-room implementation.
Tests cover empty inputs, first/middle/last matches, overlapping prefixes,
missing needles, needles longer than the haystack, and freestanding Cortex-M55
compilation. Both reviewed compilers emit the same relocation-free 46-byte
leaf with SHA-256
`66363d9e210a167b4f69d0333c9edb1d8d968311287298147705ebbcb6724a63`.
Apple places it at overlay offset 2,884/runtime `0x00434FBC`; Linux places it
at offset 2,876. The stock span is exactly replaced by `1ef0dfbf` and twenty
Thumb NOPs.

The canonical overlay is 2,930 bytes with SHA-256
`1f2ec82849242aad68a4237e81032792153da0b7939c88bc7d445a10f9afb5c6`.
The 151,530-byte provider hashes to
`e6cfa18432d3e51608a273b3e2e666f68629489e9417e0cc2c52902fc4256519`
and contains 2,923 source-owned, 3,438 generated-patch, eight alignment, and
145,161 retained authenticated bytes. It ends at `0x00434FEA`, leaving 12,310
bytes before Apollo main. The Linux provider is 151,522 bytes with SHA-256
`a365476bc664cc9201cb35e0e03bb23698e2007018b2a0c096c9099c3afda9a4`.

The canonical unsigned package is 4,733,108 bytes with SHA-256
`591f2280c97ca68dca9be07f9310b2f8c60404c04140eecc24ff304e25ac1722`;
its 4,334,189-byte flash plan hashes to
`9872769764f0c650ac51fe4cfef47da9ab3d0b7ce3dfe2ba28555ab89a1d2e7d`
and has 6,243 placed regions. The Linux package is 4,509,110 bytes with
SHA-256
`ad67d411dc72f77a5ead5178e89b75f6cd934d77d55f6e4db721fd38abcdf738`;
its 2,306,724-byte plan hashes to
`e1da97398986ac4682589bc884724c0da240f594b120205bf869d82f558476c9`
and has 3,317 placed regions. Both retain two unresolved physical-only
regions, five container-only regions, and six protected regions.

Nothing was signed, transmitted, flashed, erased, reset, or installed.
Authorized right-temple execution evidence remains unavailable, so live
EasyLogger filtering and boot progression are explicitly hardware-blocked.
This bounded closure does not establish firmware-wide functional completeness.
