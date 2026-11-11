# YHM2710 system-track C frame boundary

`board/native_yhm_system_track.c` now uses a ten-byte frame bridge around
its C logic. Native `0x355bc` saves R2/R3 as words at caller SP-16/SP-12,
clears only the low read byte, reads register one, and writes that byte
with bit one set into the low write byte. Read status remains ignored;
the final write result remains R0. The bridge restores both complete words
into R2/R3, including callback changes to their high bytes.

REA agrees with the raw instructions. The new C body uses volatile byte
stores and loads directly in the saved frame. Mode queries retain native
short-circuit/fresh-read behavior, and each enabled logger reloads the live
write byte. Existing log strings and the initialize wrapper retain exact
section bytes and relocation identities.

The previous compiler output already placed its locals at the same two
addresses, but initialized/updated them with full-word stores. A controlled
old-source replay matches R0/R2/R3 and transport values while differing in
store widths/order. The new bridge/body matches the native push stores
followed by byte-only updates. It removes dependence on compiler register
allocation around inline register moves.

The execution probe passes 83,200 stock/C comparisons. It covers every
low-three-bit mode triple, selected read bytes, four final write results,
eight mutation modes, all 256 read-byte values with absent/one/two/four-byte
callback writes, and randomized calls through the initialize wrapper.
Actual register-read frontend code executes. Lower read transport, write
boundary, mode and log callbacks are modeled and clobber caller-saved
registers. Mutations affect adjacent write bytes, live log values and both
restored words.

Checks compare exact CPU scratch-write addresses/widths/values, callback
order, owned arguments, R0/R2/R3, full saved words, callee-saved registers,
SP, masks and callback alignment. Read/log callbacks use caller SP-16 in
native and SP-32 in C. The final write boundary uses SP-16 in both.

The preexisting `r1_native_charger_initialize` source-plan selection is
also checked using its existing production compiler arguments and native
anchor/binding. Its four bytes still match the stock SHA-256. No selection
is added and the source plan is unchanged. This narrow result does not
qualify the deeper system-track body.

All 562 R1 units compile without failures or duplicate strong symbols;
the other 561 source units are unchanged. Manifest eligibility and imports
remain unchanged at 211 application / 34 bootloader, and
`make sources-check` passes. Exact bindings and regression details are in
[the machine-readable review](yhm-c-track-frame-review.json).

The C body is 108 bytes plus its ten-byte bridge, versus 106 native
instruction bytes. Private frames, arbitrary faults, exceptions,
concurrency, timing, physical GPIO/PMIC operation, final firmware linking
and whole-image byte identity remain unproven. No G2 gate changes.
