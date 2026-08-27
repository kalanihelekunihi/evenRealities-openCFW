# G2 bootloader address-identified optional runtime-notification wrapper source closure

Status: software implemented and production-routed; physical validation blocked.

Superseded as the current frontier by
`g2-bootloader-runtime-callback-41639a-source-closure.md`; the evidence below
remains the pinned notification-leaf checkpoint.

The complete 34-byte entry `[0x00416378,0x0041639A)` has SHA-256
`8a3050543e3c959ae1b5ef53792a3aa9a192000c0c82567df806bc1cdc7e51be`
and authenticated direct callers at `0x004207D6` and `0x0042E1E6`. It returns
`-6` in critical context. Outside critical context, a null argument is a
successful no-op; a non-null argument is forwarded once to retained backend
`0x00417FA8`, after which the wrapper returns zero. Address-derived names avoid
unsupported claims about the retained platform object.

`runtime_notify_416378.c` is an 891-byte GPL-3.0-or-later clean-room
implementation with SHA-256
`b9b9c16d67f56a7e06631fc6f475f11109ef43fa0822138ca4ff4866bdd22af2`.
Both reviewed compilers emit the same 28-byte, two-byte-aligned unrelocated
leaf with SHA-256
`3291144e5fa665574a5436bb84b82a0d227bea46971e44ba61ea735e5b07c391`.
Apple clang places it at overlay offset 3,714/runtime `0x004352FA`; strict
calls at offsets 4 and 20 produce relocated SHA-256
`cdeef526dc2d40b243682d65fd611b41368df125d12df677c67be987be3295c1`.
Homebrew clang 22.1.8 places it at profile offset 3,702/runtime `0x004352EE`
and produces relocated SHA-256
`af81e15c89aff539ced9c859c04c2f40e107d9c8a4f04ae88cc9be99bc191608`.
The canonical stock entry is replaced by `1ef0bfbf` plus 15 Thumb NOPs.

Host tests pin critical-context rejection, null no-op behavior, one-shot
non-null forwarding, the exact stock body and both caller edges, and target
compilation. Both reviewed toolchains compile and relocate under fail-closed
source, ABI, symbol-type, placement, and artifact pins.

The runtime tranche now contains 25 entries at
`[0x00415844,0x0041639A)`: 2,866 exact stock bytes, 128 authenticated caller
edges, 2,628 canonical compiled Thumb bytes, and 51 strict relocations. The
canonical overlay is 3,742 bytes with SHA-256
`0997c3a8b0f4c1baf6e656d9ea28c4c43e3d51c1e8ccdc70ac5b4f008c3eceec`.
The 152,342-byte provider hashes to
`cade0cc3e598d3a003db7129ebbf95f8c13f6831db3a943737b3d5d75da6b105`,
has CRC-32C/MSB `0x8E87D409`, and accounts for 3,733 source, 4,318 patch,
ten alignment, and 144,281 retained authenticated bytes. It ends at
`0x00435316`, leaving 11,498 bytes before Apollo main. The Linux overlay is
3,730 bytes with SHA-256
`ee8c8bf3089879402ebbafb6a8fd6c3530f39ae519d4056f722a04a6ca7b3f12`;
its 152,330-byte provider hashes to
`3b56bb99057e1d1dd63ecc1dc52312017fd985072106884dacf8544091111c91`.

The canonical unsigned package is 4,733,920 bytes with SHA-256
`62c3ddb78f07138b9cb39e2de4b620e80800b9eb3e20ab0731a55ca82b278a47`.
Its 4,352,754-byte flash plan hashes to
`14b19d33604d526c612230b20bcf6ca5619b3f219a8a824e7795212fe3498278`
and records 6,269 placed, two unresolved, five container-only, and six
protected regions. The independent Linux package is 4,509,918 bytes with
SHA-256
`f1b5258cf97de231f9d9442107f06e89a793e4b6b04eda3ec30a5ab91bc2491d`;
its 2,316,450-byte plan hashes to
`a445c90cc26f81735da65568c513153e71ee7b58012504fa7ac68d734a2fde85`
and records 3,330 placed regions plus the same two unresolved boundaries.

The next distinct complete callable body begins at `0x0041639A`; its entry
has no direct `BL` caller in the stock image and therefore requires stored-
pointer ingress authentication before routing. It remains a software gap. No
image was signed, installed, flashed, reset, or booted. Authorized physical
validation is blocked because the right temple is nonresponsive, the left
must remain stock, and no responsive authorized unit or equivalent trace is
available. Consequently this closure makes no live notification, critical-
context, concurrency, or caller-path claim and does not declare bootloader or
firmware-wide functional completeness.
