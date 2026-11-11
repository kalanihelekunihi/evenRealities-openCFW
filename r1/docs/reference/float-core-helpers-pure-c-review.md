# R1 trig and powf arithmetic helpers in C, 2026-11-10

The trig reducer now expresses add, subtract, multiply, multiply-accumulate,
integer-to-float conversion and negation in C. The powf reduced core now
expresses binary arithmetic, multiply-accumulate/subtract, absolute value and
integer conversions in C. The signaling zero comparison is covered by the
[subsequent C conversion](powf-zero-compare-pure-c-review.md). Together the
changes reviewed here remove twelve
`__asm__` occurrences from two C files without changing their source-owned
constant tables or manifest profiles.

The initial isolated object comparison was invalid: its command accidentally
compiled the original absolute source path. The normal manifest rebuild was
then used for the actual candidate objects. A corrected probe confirmed the
objects differ and ran the production objects against the SHA-pinned stock
image. The ignored trig fixture at
`build/r1-float-c-corrected-probe-20261110/verify_trig.py` passes **15,246**
paired cases across finite ranges, boundaries, special encodings and seven FP
control settings. It compares returned S0 bits, quadrant output, FPSCR, SP and
saved registers. The previous assembly object also passes the same fixture.

The ignored powf fixture links the production C core explicitly ahead of the
existing C dispatcher and dependency archive. It passes **4,224** stock/C
dispatcher cases over special-value combinations and seeded arbitrary words,
plus **2,048** seeded normal-range cases over four FP settings. It compares
returned S0 bits, FPSCR, public RAM and saved ABI state. These pairs cover
selected behavior, not every possible FP input or physical timing.

The source build at `build/sources-r1-float-helpers-pure-c-20261110/report.json`
compiles all 975 R1 units with no failures or duplicate strong symbols.
`make sources-check` and the strict bootloader link pass. The application
remains unlinked with 24 undefined functions and 28,328 bytes of full flash
overflow, 16 bytes above the prior checkpoint. No byte identity or hardware
boot claim follows from these tests.
