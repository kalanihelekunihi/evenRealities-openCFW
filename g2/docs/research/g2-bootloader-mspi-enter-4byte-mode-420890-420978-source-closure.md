# G2 bootloader MX25U25643G enter-four-byte-mode source closure

> **Superseded temple-status premise:** Treat temple nonresponse/unavailability
> claims below only as history. The case was bumped during lunch and caused the
> disconnect, not firmware or flashing; exclude it from feasibility conclusions.
> Hardware testing remains blocked by unavailable physical evidence.

The complete authenticated function `[0x00420890,0x00420978)` is now routed
to compilable clean-room C as
`open_cfw_bootloader_mspi_enter_4byte_mode_420890`. The 232-byte stock body
has SHA-256
`ad4285ffa57c4bd7999a6b83f2bb9569b6bb85e40ef419b42bde4514d3f7e50c`;
its sole direct caller is the authenticated Thumb call at `0x00420512`
(`00f0bdf9`). The preceding `[0x0042086C,0x00420890)` literal region is 36
bytes with SHA-256
`bd568192057107608070c8993444e0e2bdc34243a5ddf9972040371697be4eca`
and remains classified as retained non-executable compatibility data.

The implementation preserves the stock state machine and status quirks. It
rejects an unavailable MSPI handle with status 2, maps an initially busy
device to status 3 and its exact diagnostic, propagates raw write-enable and
command failures, issues command `0xB7`, performs but ignores the second ready
poll result, and treats every nonzero address-mode read result as success. A
zero verification result emits the stock failure diagnostic and returns 1.
The final write-disable status is propagated; otherwise the function returns
zero. Host tests pin every branch, call order, diagnostic tuple, fixed address,
and the deliberate post-command quirks.

Apple Clang 21.0.0 emits a relocation-free 220-byte leaf at `0x00437678`
with SHA-256
`041427a167b5b0379af8d927c7ab094274fcd542b67cfe5a0deaccbd885571e4`.
Linux Clang 22.1.8 emits a relocation-free 220-byte leaf at `0x00437668`
with SHA-256
`5b671b715da7b544fbbab9cd3198ea11a6f5629e2ad03ce730e5f47e2f9d197c`.
The canonical provider is 161,620 bytes with SHA-256
`25b1d6a8b3bda1d7cd4b28dab6472d7820f800bc3690bb2306f2b5cbd661880e`;
the Linux replay is 161,604 bytes with SHA-256
`e54af73c579e7f2749a696cf6d1eb34a7536d6b036f09730e63e03cea44ceee2`.
The unsigned canonical package is 4,743,198 bytes with SHA-256
`f7d74c7ae574671b3677c8b94500305482fd89180e17eaa367c9358caaff44e7`.

No hardware operation was performed. Live command, status-register, MSPI,
external-flash, XIP, write-enable-latch, and cold-boot behavior remain
explicitly blocked by the absence of an authorized responsive right-temple
G2; the left temple must remain stock. The immediately following write-latch
wrappers were subsequently source-closed separately; retained executable
bodies beginning at `0x00420A08` still prevent a functional-completeness
claim. See the
[write-latch closure](g2-bootloader-mspi-write-latch-420984-4209fc-source-closure.md).
