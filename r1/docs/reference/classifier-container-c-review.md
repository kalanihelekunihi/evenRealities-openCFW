# Four-word classifier results expressed in C

`native_float_bits.c` and its shared header now express the native binary32
and binary64 classifier result as a typed four-word C container. Explicit base
PCS lowers it to R0-R3 on the qualified M4 target: tag, auxiliary word, limit,
and preserved incomingR3. Two empty assembly blocks and eight named-register
bindings are removed. The module now contains no inline assembly.

All11 C consumers select the tag from lane0 using the shared declaration.
Nine caller objects remain byte-identical. GCC sinf/tanf have changed private
register saves, growing each entry frame from24 to40 bytes; their outputs and
architectural state pass264,960 staged and49,680 normal-object comparisons.

Stock execution at `0x38110`/`0x38140` matches851,968 classifier cases under32
FP configurations. Checks include all four return words, every FP register,
saved core registers, full FPSCR, SP and masks. Independent tag/auxiliary-word
oracles cover6,144 binary32 inputs and20,480 binary64 inputs, including every
exponent field, both signs and random payloads. All34 instruction starts /86
native body bytes execute.132 additional leaf comparisons pass with FPU access
disabled. Full math remains separately primed; physical boot is untested.

Six compiled defects are rejected: lost incomingR3, wrong binary32 auxiliary,
wrong binary64 limit, omitted low mantissa, sign treated as exponent and wrong
binary64 auxiliary. An omitted PCS annotation produces identical probe code
under this profile; it is recorded as neutral, not counted as a rejected defect.

All927 normal units compile and compose without failures or duplicate strong
symbols. All12 edited objects match staged sections and decoded symbols.904
unrelated source/object pairs are byte-identical. One unmodified GoMore helper
changes only four compiler-generated local-label strings; exact string-table
replacement proves the entire remaining object is byte-identical, including
code/data/relocations and symbol records. No executable/data bytes are normalized.
Only the binary64 classifier section changes in the provider; its other functions
and data remain unchanged. Named math tables, source plan and health-cache layout
are preserved. Imports remain72 application /22 boot.

[Machine-readable evidence](classifier-container-c-review.json) pins sources,
originals, compiler profiles, tests and the precise label audit. Private8192-byte
frames and caller-clobbered R12/APSR are outside full caller proof. The C container
and PCS annotation are compiler extensions; other profiles require qualification.
Hardware stack limits, timing, interrupt behavior, source startup, five remaining
callback bindings and complete firmware boot remain open.
