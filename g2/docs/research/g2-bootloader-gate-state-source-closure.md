# G2 bootloader runtime-state gate mapper source closure

Status: software implemented and production-routed; physical validation blocked.

Aggregate package and accounting values below record this historical
checkpoint and are superseded by the gate-release closure that follows.

The complete 40-byte entry `[0x00416088,0x004160B0)` has SHA-256
`0fb1ec985d7caf9e9575909ee1fcf3c7c7941be48737826c41c28d29b266bc87`
and one authenticated direct caller at `0x004207CC`. It calls the retained
runtime-state query at `0x00418B56` exactly once. State zero maps to three and
state two maps to two without reading the SRAM gate word. All other states
map to one only when the word at `0x200270D4` equals one, and to zero
otherwise. Host tests pin all four outputs, both short circuits, call counts,
and the exact single-caller topology.

`runtime_gate_state.c` is a 728-byte GPL-3.0-or-later clean-room
implementation with SHA-256
`00a4c79c1c86741449d711f14ef8c9d3e77de043171374a7a943028c597448f9`.
Apple clang emits a 36-byte, four-byte-aligned leaf at overlay offset
3,024/runtime `0x00435048`. Its unrelocated SHA-256 is
`9aaba73e4502c325ee98f7b8106ce0df23fe3bec18fd9ad10a6da75061b1eb0d`
and its relocated SHA-256 is
`cf55382094cbfa576d7a227ee6f713b4117721589a56811148ac7d31d7d7e46d`.
The only strict relocation is an `R_ARM_THM_CALL` at offset two to the
retained state query; the fixed SRAM address is emitted as an in-text literal.
The stock body is replaced exactly by `1ef0debf` and 18 Thumb NOPs.
Homebrew clang 22.1.8 emits the same raw body at profile offset 3,016, with
relocated SHA-256
`a7ef6e886972f68a65df2a98dace67ca4fa119ff547e76a2934afccc7435ea17`.

The canonical overlay is 3,060 bytes with SHA-256
`c9e5bea4fd7ddfae8b565b376c7e1f8118da7aaa4984f0e298804dcdee9af099`.
The 151,660-byte provider hashes to
`a03583a97e367b9301168028d890a326594c3eac1aab2ba097a3e6cb25308c30`,
has CRC-32C/MSB `0x62637DE1`, and accounts for 3,053 source, 3,572 patch,
eight alignment, and 145,027 retained authenticated bytes. It ends at
`0x0043506C`, leaving 12,180 bytes before Apollo main. The Linux overlay is
3,052 bytes with SHA-256
`163c3ee82016b8a6684519d33898f11c76555b3957ecec248aa70b8f6959fb0d`;
its 151,652-byte provider hashes to
`19be9241cc4463003acee3f1bfb12939dd6bebe42f86189c389fac52cf02a0c8`.

The canonical unsigned package is 4,733,238 bytes with SHA-256
`4b59f8c2e7b8ee49974b8a2bd41eaac65fc1eb1f385e0b2e0514faf28a85a37d`.
Its 4,339,077-byte flash plan hashes to
`98ecc236662e88e372fa598665aa6d06b5c07ee10bf34033fc21b9367f10dac4`
and records 6,250 placed, two unresolved, five container-only, and six
protected regions. The independent Linux package is 4,509,240 bytes with
SHA-256
`62d47b97891d6da4d832ae5755791215844a66de2dd59082bbbc7d4c04c6a6df`;
its 2,309,627-byte plan hashes to
`b5b9ede2a3fb36cdf8aa87076e37715a131ad84eb2e69c51eeee4cdc359fc2c8`
and records 3,321 placed regions plus the same two unresolved boundaries.

The next distinct 56-byte callable body begins at `0x004160B0`; it remains a
software gap. No image was signed, installed, flashed, reset, or booted.
Authorized physical validation is blocked because the right temple is
nonresponsive, the left must remain stock, and no responsive authorized unit
or equivalent trace is available. Consequently this closure makes no live
runtime-state, gate, or concurrency claim and does not declare bootloader or
firmware-wide functional completeness.
