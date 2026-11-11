# GXT310 one-shot trigger in C

Native `r1_gxt310_one_shot` at `0x6f738` now delegates its logic to a C body
in `runtime/native_temperature.c`. A ten-byte frame bridge retains the
command word at caller SP-16 and restores its full value into R3, including
callback changes. C writes `0x0000c101` to that word and calls the existing
transfer provider with `(address, 1, frame, 2)`.

Stock returns one immediately for a nonzero transfer result. A zero result
continues through logging and returns zero. The C implementation preserves
this behavior despite the failure wording of the log strings. Log mode is
read once for bit zero, again for bit two only if needed, then freshly for
SDK bit one. The structured log uses severity `0x04400000`, the same string
for both format pointers and the full address argument. The SDK log uses
`0x001c0001`, derived from native bounds `0xc44fc` and `0xc441c`.

REA and raw instructions agree on this sequence. The execution probe passed
8,448 stock/C comparisons, covering all 512 triples of low-three-bit log
modes, four transfer statuses, both channel addresses, unchanged/mutated
command words, plus randomized full-width inputs and modes. The transfer,
mode and log callbacks are modeled and clobber caller-saved registers.
Checks compare callback sequence, owned arguments, R0, restored R3 and
command bytes; verify initial command, callee-saved registers, SP and masks;
and require eight-byte callback alignment. Both source strings match stock.

All other temperature function/data sections retain their bytes and
relocation identities, including the preceding C pair and conversion work.
The other 561 source units are unchanged. All 562 R1 units compile without
failures or duplicate strong symbols. Manifest eligibility and imports
remain unchanged at 214 application and 34 bootloader imports, and
`make sources-check` passes.

The C body is 96 bytes plus its ten-byte bridge; native instructions occupy
92 bytes. Callback SP changes from caller SP-16 to SP-32 while retaining
the command pointer at SP-16. Private frame, faults, exception behavior,
timing, physical bus/log delivery, final firmware linking, qualification
and whole-image byte identity remain unproven. No G2 gate or source-plan
selection changes.

Exact bindings are in [the machine-readable review](temperature-c-trigger-review.json).
