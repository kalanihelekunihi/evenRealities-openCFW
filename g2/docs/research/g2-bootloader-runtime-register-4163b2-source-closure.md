# G2 bootloader address-identified registered runtime-object constructor source closure

Status: software implemented and production-routed; physical validation blocked.

The complete 232-byte entry `[0x004163B2,0x0041649A)` has SHA-256
`3d816e28d9db37c7ac113ab48791bf1b0d790e7b6d04e3dc0eaef95b37a601f1`
and one authenticated direct caller at `0x0042E590`. It rejects critical
context and a null owner with a zero result. It selects an embedded eight-byte
callback record at storage offset 44 only when at least 52 bytes are supplied,
otherwise allocates eight bytes through retained provider `0x00419730` and
tags that record in bit zero. The record receives the owner and argument.

The recovered four-word configuration preserves the stock distinction between
static registration (non-null storage of at least 44 bytes), dynamic
registration (null storage with zero size), and an invalid mixed configuration.
Static and dynamic modes call retained backends `0x004192DE` and `0x004192A8`
with count one, the low-byte Boolean option, the tagged record, and callback
entry `0x0041639B`; static mode also forwards the storage base. A failed
registration frees only a dynamically allocated record, after clearing its
tag, through retained provider `0x00419830`.

`runtime_register_4163b2.c` is a 5,261-byte GPL-3.0-or-later clean-room
implementation with SHA-256
`4673227907a6cf5757607fe2d577991fab914dc9e7823d4fcd9073a48cdecacf`.
Apple clang emits a 180-byte, four-byte-aligned unrelocated leaf with SHA-256
`72e4dc512eb470a9b9fde5899268fe63fd0d9fc48a318051bcb11d767f88456f`.
After two alignment bytes it is placed at overlay offset 3,768/runtime
`0x00435330`; five strict calls at offsets 12, 62, 112, 140, and 168 produce
relocated SHA-256
`cf36ee9b633b21351999ab045989ac337713b18185cedacb9f2610535e42a88b`.
Homebrew clang 22.1.8 emits a 176-byte unrelocated leaf with SHA-256
`92150362990f6f77c8033adf983cbf6f0620ba37ad0a801e562456423b57354d`.
After two alignment bytes it is placed at profile offset 3,756/runtime
`0x00435324`; profile relocation produces SHA-256
`f201551d621e522520735f876f2200df72734220aeac0d8b7c74315dbe1ca473`.
The canonical stock entry is replaced by `1ef0bdbf` plus 114 Thumb NOPs.

Host tests pin critical/null/allocation short circuits, dynamic tagged-record
construction, exact owner/argument words, low-byte option conversion, callback
entry forwarding, success ownership, failure-only free, embedded static
storage, invalid mixed configuration cleanup, the complete stock body, caller,
and target compilation. Both reviewed toolchains compile and relocate under
fail-closed source, ABI, symbol-type, placement, and artifact pins.

The runtime tranche now contains 27 entries at
`[0x00415844,0x0041649A)`: 3,122 exact stock bytes, 129 authenticated direct
caller edges, two registered-pointer ingress paths, 2,832 canonical compiled
Thumb bytes, and 57 strict relocations. The canonical overlay is 3,948 bytes
with SHA-256
`d061e8f101dbde9ce03fd44a0ef0441b04f8e0290746de917ad24f77542f1d77`.
The 152,548-byte provider hashes to
`6f1c62ab2619d5e19daf3e61340f876cb8b54581e15bccdb0d45a9865fc3cf3b`,
has CRC-32C/MSB `0x5D3B2394`, and accounts for 3,937 source, 4,574 patch,
12 alignment, and 144,025 retained authenticated bytes. It ends at
`0x004353E4`, leaving 11,292 bytes before Apollo main. The Linux overlay is
3,932 bytes with SHA-256
`18b9bee7634609ceea777ffb1522f02c454e4285ec3cf7c639f14b1ce8fabfaa`;
its 152,532-byte provider hashes to
`0d36ffe9df007558b5841cf8ca310496488402b9c10e0944d5f1b11f1c90a991`.

The canonical unsigned package is 4,734,126 bytes with SHA-256
`92d15edd66cb8aca3ab01906e7eeec8470736ed7c810dbad1c516c13bc57e6bd`.
Its 4,356,424-byte flash plan hashes to
`a0fd7df302620f82f19bcc2fd50cfefe3226cb01fb8fbc80b444db023b7bdb33`
and records 6,274 placed, two unresolved, five container-only, and six
protected regions. The independent Linux package is 4,510,120 bytes with
SHA-256
`449d3cf6f116bda6a9ef4229765c591409a732515a2c8a4867360d901af39f34`;
its 2,318,003-byte plan hashes to
`c233e9eed03c2b5253ba60587504bd21ca4317741f83c68546669de197d9ffd6`
and records 3,332 placed regions plus the same two unresolved boundaries.

The next distinct complete callable body begins at `0x0041649A`; it remains a
software gap. No image was signed, installed, flashed, reset, or booted.
Authorized physical validation is blocked because the right temple is
nonresponsive, the left must remain stock, and no responsive authorized unit
or equivalent trace is available. Consequently this closure makes no live
registration, scheduling, allocation, concurrency, or caller-path claim and
does not declare bootloader or firmware-wide functional completeness.
