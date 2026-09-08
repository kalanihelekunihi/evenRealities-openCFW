# GX8002 I2S register setters

Date: 2026-09-07. Three additional codec functions now supply compiled C in
the experimental firmware: `gx_audio_in_set_i2s_clock`,
`gx_audio_in_set_i2sin_mode`, and `gx_audio_in_set_i2sout_mode`.

Each reads one 32-bit register, replaces a field, writes once, and returns
zero. The clock field is bits 26:24 at `0xA0A00000`; input mode is bit 16 at
`0xA0A00004`; output mode is bit 4 at `0xA0A00008`. Inputs are truncated to the
field width, including non-boolean mode values. All unrelated bits survive.
These details were checked in authenticated SDK object sections that match
both firmware images, alongside the corrected Ghidra output.

The C implementation uses a local union with unsigned bitfields, then writes
its complete word to a volatile MMIO pointer. The bitfield object itself is
not volatile and does not directly alias MMIO. This preserves exactly one
hardware read and write while allowing GCC to emit the original `ins`
instruction. Explicit mask/shift C produced larger sequences in this compiler.

Bitfield layout is implementation-defined. Qualification therefore compares
every target instruction with the authenticated original, permitting only a
consistent permutation of caller-saved scratch registers r1/r2/r3. Argument
and return register r0, instruction order, immediates, addresses, and field
bounds cannot change. Both sides contain precisely `movih`, `ld.w`, `ins`,
`movi`, `st.w`, and `rts`. All three target sections are 16 bytes with no
relocations or undefined symbols. The [report](gx8002-i2s-source-verification.json)
pins source and target hashes and records the accepted register mapping.

Host tests additionally execute 12,435 boundary/random cases, checking field
truncation and preservation of unrelated registers. Admission tests reject
argument-register changes, field-bound changes, and reordered accesses.

Rebuild with `make -C g2 gx8002-source-candidate`, then
`make -C g2 codec-source-experimental`. The complete codec candidate now has
564 compiled C bytes, 80 generated metadata bytes, and 325,448 retained stock
bytes. The six new occurrences replace 96 stock bytes. Whole-device behavior
remains unqualified; this is still a hybrid intermediate, not source-only
completion.
