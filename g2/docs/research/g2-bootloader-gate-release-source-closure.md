# G2 bootloader runtime-state gate release source closure

Status: software implemented and production-routed; physical validation blocked.

The complete 56-byte entry `[0x004160B0,0x004160E8)` has SHA-256
`e5df2dd5abb60c81887e7754bca2eef18621d559e28482dcce5ffaf887993678`
and one authenticated direct caller at `0x0042E3C4`. A nonzero result from
the source-owned critical-context predicate returns `-6`. Otherwise, a
retained runtime state other than one or an SRAM gate word other than one
returns `-1`. The success path calls the retained no-op compatibility hook at
`0x00416028`, writes two to `0x200270D4`, calls the retained completion entry
at `0x00418148`, and returns zero. Host tests pin every short circuit, error
code, mutation, callback count, and hook/store/completion order.

`runtime_gate_release.c` is a 1,464-byte MIT clean-room
implementation with SHA-256
`fad09dc4b325b04a0b1ddec21847565672a094ce18a2dfb03244a5598a0ef3ef`.
Apple clang emits a 56-byte leaf at overlay offset 3,060/runtime
`0x0043506C`. Its unrelocated SHA-256 is
`b7155e159118a2ab6e72199d3848523e2e6d1d498e767bf9df662a02e06ede20`
and its relocated SHA-256 is
`50993e787f6920b6c35eba177f2c35c45326b6173d0b0a9ebcf91727edcfd3fb`.
Four strict `R_ARM_THM_CALL` relocations at offsets 2, 14, 30, and 38 bind
the source-owned context predicate, retained state query, retained no-op hook,
and retained completion entry. The stock body is replaced exactly by
`1ef0dcbf` and 26 Thumb NOPs. Homebrew clang 22.1.8 emits the same raw body at
profile offset 3,052, with relocated SHA-256
`425de0eb2ae0368edf6c4afd9df1a10a090d2960bb6d6c505864a9277515cffb`.

The aggregate package and accounting values below record this historical
checkpoint and are superseded by the context-value closure that follows.

The canonical overlay is 3,116 bytes with SHA-256
`f40da8226f8e70bb1d1d1d48007d0f57915e3197aa1d313c498a90be767edd60`.
The 151,716-byte provider hashes to
`804d8640fff4e66d134bf6cb34970faea690d07047188fd32e4f715df79387cd`,
has CRC-32C/MSB `0xD52F6B8C`, and accounts for 3,109 source, 3,628 patch,
eight alignment, and 144,971 retained authenticated bytes. It ends at
`0x004350A4`, leaving 12,124 bytes before Apollo main. The Linux overlay is
3,108 bytes with SHA-256
`e46e179b82aa2e5eac3d30e7adc762ba5364fd21ead8818318ec1f2fa7eae462`;
its 151,708-byte provider hashes to
`032ff02d026825201cfe9d4c59c4e57fec352ebe99c13adff7d6655739776ae6`.

The canonical unsigned package is 4,733,294 bytes with SHA-256
`664a3723e872e1fbe03e7b9237de770cb526e78d8ad9bea1f43fd0cded1cf42d`.
Its 4,340,470-byte flash plan hashes to
`c1ad880cf2d1ced3eaebf564a009e4ff0ececcd90dd26b40cb383c05f3a7e3a4`
and records 6,252 placed, two unresolved, five container-only, and six
protected regions. The independent Linux package is 4,509,296 bytes with
SHA-256
`91c5674557403e21518678e81e432abbaa0ca2085d1f9a0d69be876197d8823d`;
its 2,310,360-byte plan hashes to
`ad144e986ea14e305a566e827fd5a053af9eea66003193fbdd3f6cdb621afbf4`
and records 3,322 placed regions plus the same two unresolved boundaries.

The next distinct 22-byte callable body begins at `0x004160E8`; it remains a
software gap. No image was signed, installed, flashed, reset, or booted.
Authorized physical validation is blocked because the right temple is
nonresponsive, the left must remain stock, and no responsive authorized unit
or equivalent trace is available. Consequently this closure makes no live
runtime-state, gate, hook, completion, or concurrency claim and does not
declare bootloader or firmware-wide functional completeness.
