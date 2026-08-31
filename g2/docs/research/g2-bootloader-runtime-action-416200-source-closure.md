# G2 bootloader address-identified guarded runtime-action wrapper source closure

> **Superseded temple-status premise:** Treat temple nonresponse/unavailability
> claims below only as history. The case was bumped during lunch and caused the
> disconnect, not firmware or flashing; exclude it from feasibility conclusions.
> Hardware testing remains blocked by unavailable physical evidence.

Status: software implemented and production-routed; physical validation blocked.

Superseded as the current frontier by
`g2-bootloader-runtime-transfer-41623a-source-closure.md`; the measurements
below remain the authenticated action-wrapper checkpoint.

The complete 58-byte entry `[0x00416200,0x0041623A)` has SHA-256
`e4c78725081eb02641d1918a3879468520998e6bc55183b1115b2f130a39bf28`
and authenticated direct callers at `0x0042DDE8`, `0x0042E3D6`, and
`0x0042E5FE`. It returns `-6` in critical context, `-4` for a null argument,
and `-3` when the low byte returned by retained predicate `0x00417FE4` equals
four. Otherwise it forwards the exact argument to retained action
`0x00417F0A` and returns zero. Address-derived names avoid unsupported claims
about the retained platform objects.

`runtime_action_416200.c` is a 1,369-byte MIT clean-room
implementation with SHA-256
`9e3ea4bfddd8479be954e13c8d2a07b58c5c485dfcc35f77f2048aa20db04388`.
Both reviewed compilers emit a 52-byte leaf with unrelocated SHA-256
`fe4a2a6ca7ed0e969f2baa8ea0c7a851701db79524997a285aa5445b593c8c06`.
Apple clang places it at overlay offset 3,354/runtime `0x00435192`; three
strict calls at offsets four, 20, and 38 produce relocated SHA-256
`b2b46070c4672ec7c9432320a1ba5599b6ed0163cc18b7f2debec36a4466c699`.
Homebrew clang 22.1.8 places it at profile offset 3,344/runtime `0x00435188`
and produces relocated SHA-256
`92e578bd2f5d64ded54496efca8d4d929de2f39568fad0955d071d399cd2dac0`.
The stock entry is replaced by `1ef0c7bf` plus 27 Thumb NOPs.

Host tests pin critical and null short-circuits, low-byte truncation for the
predicate result, exact argument forwarding, and predicate/action call counts.
Both toolchains compile and relocate under fail-closed source, ABI,
symbol-type, and artifact pins.

The runtime tranche now contains 22 entries at
`[0x00415844,0x0041623A)`: 2,514 exact stock bytes, 121 authenticated caller
edges, 2,294 canonical compiled Thumb bytes, and 40 strict relocations. The
canonical overlay is 3,406 bytes with SHA-256
`95ad316d1927e52227ecf4a0eada8b74da5c8923afd681452743db680acd4691`.
The 152,006-byte provider hashes to
`bfb89bc0ced9e5a186fdd1fadcbd7402611104e0df04d7257d4566bb529325f3`,
has CRC-32C/MSB `0x127431F1`, and accounts for 3,399 source, 3,966 patch,
eight alignment, and 144,633 retained authenticated bytes. It ends at
`0x004351C6`, leaving 11,834 bytes before Apollo main. The Linux overlay is
3,396 bytes with SHA-256
`a72258cd2385a97b9f28b009e621eb4126f6dcbe13e193049d8737caa4634b58`;
its 151,996-byte provider hashes to
`e79f356d097213665d96ccab6860184524c1da3d164a6a5eb084a3b2d43e43cf`.

The canonical unsigned package is 4,733,584 bytes with SHA-256
`7c2fa015431f27161a9af1261f31d67d36b4f052d73b8e7cf1d57bfd1e8d9058`.
Its 4,347,663-byte flash plan hashes to
`8c2eb1d8708403b9a0286ac4623e24f7dd7401c7d04a34b99cb2b65f696cf358`
and records 6,262 placed, two unresolved, five container-only, and six
protected regions. The independent Linux package is 4,509,584 bytes with
SHA-256
`b269150095d9ddedb297b707323173bfdde2e1a33dda66d65121ee289d1e8e56`;
its 2,314,142-byte plan hashes to
`8dadfa6dfa7d7357dfc67a85ead94cd94593c76434a1184ddb78bd1f28e3f3fd`
and records 3,327 placed regions plus the same two unresolved boundaries.

The next distinct complete callable body begins at `0x0041623A`; it remains a
software gap. No image was signed, installed, flashed, reset, or booted.
Authorized physical validation is blocked because the right temple is
nonresponsive, the left must remain stock, and no responsive authorized unit
or equivalent trace is available. Consequently this closure makes no live
predicate/action, caller-path, or concurrency claim and does not declare
bootloader or firmware-wide functional completeness.
