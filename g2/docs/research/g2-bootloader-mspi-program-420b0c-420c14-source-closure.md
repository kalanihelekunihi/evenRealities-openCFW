# G2 bootloader MX25U25643G page-program source closure

The complete authenticated page-program function `[0x00420B0C,0x00420C14)`
is now routed to compilable clean-room C. The 264-byte stock body has SHA-256
`dcaf2a13af5fb811c228b4845363682411abf1acab703507368f6d1e4463b15e`.
Its sole direct caller is the Thumb `BL` at `0x00421326`. The 50-byte
predecessor pool/gap `[0x00420ADA,0x00420B0C)` remains authenticated retained
data with SHA-256
`619fd98be5ccc3286a0a39c06f1c556503edee5868456a01e8e15c67b2fb5ed2`;
the 72-byte successor pool `[0x00420C14,0x00420C5C)` hashes to
`cfc3cdfaf2523ca39c957109635e3427aa5dca5f88993d6b841bc3ebc21b760f`.

The maintained implementation rejects an unavailable device handle, null
buffer, or zero length with status 6 and the exact stock three-argument
diagnostic. A starting address at or above `0x02000000` returns status 5.
Valid requests enter the MSPI guard, switch to serial mode, and divide the
payload at 256-byte page boundaries. Each chunk performs fixed ready polling,
write enable, command `0x02` with address flag 1 and the exact data slice, a
ready poll bounded by 10 slow iterations, and write disable. Fixed and bounded
poll failures map to status 4; command-stage failures preserve their raw
status. Every guarded exit restores quad mode and releases the guard.

Host tests pin validation, both retained pools, the sole caller, first-page
offset arithmetic, multi-page address/buffer/length advancement, the complete
transfer tuple, all five staged failure paths, later-page failure context,
diagnostics, cleanup ordering, success, and a Cortex-M55 freestanding
cross-compile. Both Apple Clang 21.0.0 and Linux Clang 22.1.8 emit the same
relocation-free 256-byte leaf, SHA-256
`1d90e6749de44a32ff7a6b4ced694569bf95e4b836961891cde35edf06f6e482`,
at `0x004378D8` and `0x004378C8`, respectively.

Canonical and Linux overlay identities are 13,664 / 13,648 bytes with
SHA-256
`9b72a887df63cd94a36c45d73f8c1237e34db734b2c8dd91a4797110d3d8a395`
and `ff1a490411cd440468370bc2b822ffd5a1673efbaad8ba504aa0a27afff379fa`.
Provider identities are 162,264 / 162,248 bytes with SHA-256
`d02333f0a79d6d9d3fe5918330ffaa1365691dda1420fdad2165fb956b5cb7fb`
and `5b7fd6cbdf5205c1292226e6eebe21cd2a8c0bff684dc9dfb4f9af114dd79b21`.
Canonical accounting is 13,649 source-owned, 14,918 generated patch, 16
alignment, and 133,681 retained official bytes across 189 functions, 170
relocated leaves, and 187 patch sites. The unsigned canonical package is
4,743,842 bytes with SHA-256
`1f3191b816b1e30cb82cd06653f63514a2174eebd942b44b92cf43152c4769dd`;
its 4,546,078-byte flash plan hashes to
`e2b4c63d1e6cc522495a82f2dac12ff48f2373cce95a16ff5ccebb7da67339ef`
and contains 6,534 placed regions plus two unresolved physical boundaries.

No signing, flashing, installation, reset, boot, program command, or other
hardware operation was performed. Live page programming, write-latch, MSPI,
external-flash, XIP, error-path, and cold-boot validation remains explicitly
blocked by the absence of an authorized responsive right-temple G2; the left
temple must remain stock. The next authenticated executable function begins at
`0x00420C5C` and remains a software source-closure frontier. This is not a
firmware-wide functional-completeness claim.
