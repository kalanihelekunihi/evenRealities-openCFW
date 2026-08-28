# G2 bootloader critical-context value-dispatch source closure

Status: software implemented and production-routed; physical validation blocked.

The complete 22-byte entry `[0x004160E8,0x004160FE)` has SHA-256
`4fe35d35c5f61f5683c7ddd34f424d7f51d8a9276a0249c71b8473811dc7890a`
and authenticated direct callers at `0x0041A6AC`, `0x0042E382`, and
`0x0042E82C`. It calls the source-owned critical-context predicate. A nonzero
result tail-dispatches the retained getter at `0x00418362`, which reads
`0x20026F5C`; zero tail-dispatches the retained getter at `0x0041835A`, which
reads `0x20027148`. Host tests pin both dispatch paths and the exact caller
bytes without assigning unsupported semantic names to the two retained SRAM
values.

`runtime_context_value.c` is a 983-byte MIT clean-room
implementation with SHA-256
`9e7720908c8770722bbfe763d5b11e2dea0fb6792edb64a427174c52bbe616bb`.
Apple clang emits a 24-byte leaf at overlay offset 3,116/runtime
`0x004350A4`. Its unrelocated SHA-256 is
`563b6ab3fb7c401ccbd66a3b12963c9134ec11f7c148a149ae70f20f74d1da23`
and its relocated SHA-256 is
`51c966c09d177c46ea7a0c26fa51a8ba1d1b16f38ced900b733e9641ef9218da`.
An `R_ARM_THM_CALL` relocation at offset 2 binds the source-owned predicate;
`R_ARM_THM_JUMP24` relocations at offsets 12 and 20 bind the retained critical
and normal getters. The stock entry is replaced exactly by `1ef0dcbf` and
nine Thumb NOPs. Homebrew clang 22.1.8 emits the same raw body at profile
offset 3,108, with relocated SHA-256
`ec020452cd132b873199e18a8c04879adc61552f3c1832e6fb71f3ce25b2bb79`.

The aggregate package and accounting values below record this historical
checkpoint and are superseded by the `0x004160FE` runtime-dispatch closure.

This closes eighteen numeric, formatter, logging-dispatch, string, context,
gate, and value-dispatch entries at `[0x00415844,0x004160FE)`: 2,198 exact
stock bytes, 111 authenticated caller edges, 2,028 compiled Thumb bytes, and
31 strict relocations. The canonical overlay is 3,140 bytes with SHA-256
`3acbd7c2dd0275b9c12e66adc9d725c96c81ad54f3f0ccbcaca2e36764f5d62a`.
The 151,740-byte provider hashes to
`c1fade15b3a16c8d273a5548bfac6b019232278cd3a5ee035e26cf84deed4621`,
has CRC-32C/MSB `0xDAC445D3`, and accounts for 3,133 source, 3,650 patch,
eight alignment, and 144,949 retained authenticated bytes. It ends at
`0x004350BC`, leaving 12,100 bytes before Apollo main. The Linux overlay is
3,132 bytes with SHA-256
`64e84956820a822e101d32734c185f1a98160f0972a28842dc6e4d43df940378`;
its 151,732-byte provider hashes to
`aaf8757121b811183c9b7bb448903b904ec8fe56aa91eb3c8d60dcec4c06918d`.

The canonical unsigned package is 4,733,318 bytes with SHA-256
`868f088fb62d1072c3cc4576adf18ad4ee1073dc7093129da3bfa7c00aee6232`.
Its 4,341,871-byte flash plan hashes to
`dd7a192bee67ed2a7b5496c2460314630e28f6e6cdbea529cd3712a919c36567`
and records 6,254 placed, two unresolved, five container-only, and six
protected regions. The independent Linux package is 4,509,320 bytes with
SHA-256
`c46202fa55a80c6099ddb9f6dedd50f8b038079f77b3957b4a98aeed96ead3e3`;
its 2,311,100-byte plan hashes to
`f4b597ef396a46bd0d73898a9cc661e77dadad8e6e6196b00a4b8ba4cbda2581`
and records 3,323 placed regions plus the same two unresolved boundaries.

The next distinct complete callable body begins at `0x004160FE`; it remains a
software gap. No image was signed, installed, flashed, reset, or booted.
Authorized physical validation is blocked because the right temple is
nonresponsive, the left must remain stock, and no responsive authorized unit
or equivalent trace is available. Consequently this closure makes no live
critical-context, getter-state, caller-path, or concurrency claim and does not
declare bootloader or firmware-wide functional completeness.
