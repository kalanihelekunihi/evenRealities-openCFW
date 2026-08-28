# G2 bootloader MX25U25643G soft-reset source closure

The complete authenticated 116-byte entry `[0x0042052A,0x0042059E)` now
routes to `open_cfw_bootloader_mspi_soft_reset_42052a` in maintained clean-room
C. The stock SHA-256 is
`ec592b1db3c6c381036d5c69d065056547b69d870025dd08aef11f34c2b350f0`;
the 3,305-byte source SHA-256 is
`ebe83fc0c63dc78e6c165f308dfd331eaf9cdc0a171c036a564f581d55bd3b47`.

Stock and host evidence pins reset-enable command `0x66`, a 1-ms delay, reset
command `0x99`, a 50-ms delay, failure-only logging for both commands, and the
non-short-circuiting policy. Both profiles emit a 136-byte leaf with strict
call and tail-jump relocations to the source-owned delay wrapper. Apple places
it at offset 11,932/runtime `0x00437314`, with raw/final SHA-256
`1223a14bfe9fc5267517253e84772bf9eb52ce7d760f563db26fd342d838a468` /
`17354876de75a9540cac0603e3f8eae3fbd564a239c0d07f771b1104065c817c`.
Linux places it at offset 11,912/runtime `0x00437300`, with raw/final SHA-256
`2d4513df2ad6e6bb485e65d393dfda276ace283a014ea8226cbcbd85c339d7bf` /
`19f375dd75796c0b77410e90c9a6a813e26899aa68a58af6176b72d57db1ce69`.

Apple/Linux overlay/provider identities are 12,068/160,668 and
12,048/160,648 bytes. Canonical accounting is 12,053 source-owned, 13,380
generated patch, 16 alignment, and 135,219 retained official bytes across 177
routed functions, 158 relocated leaves, and 175 patch sites. Unsigned
Apple/Linux packages are 4,742,246 / 4,518,236 bytes with SHA-256
`27849e7bbbfee7f4a9330f34b6cb9a311e336dbfad446d39675c8f6288cc15ee` /
`22ececac9f2cba0ff15552a9d719913ae9840002dc5d1878e10d19c09e289fd2`;
their flash plans contain 6,505 / 3,453 placed regions.

Nothing was signed, flashed, installed, reset, booted, or sent to hardware.
Live command acceptance, reset timing, JEDEC/MSPI/XIP/external-flash, and cold
boot validation is blocked because no authorized responsive right G2 temple
is available; the left temple must remain stock. Executable bodies after
`0x0042059E` remain software gaps, so firmware-wide completeness is not
claimed.
