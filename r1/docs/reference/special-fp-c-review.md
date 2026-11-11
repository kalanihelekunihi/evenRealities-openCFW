# R1 shared special-value arithmetic in C

`native_math_special32.c` replaces the six single-precision assembly functions
formerly in `native_math_special.c`: positive infinity/divide-by-zero, self-add,
pair add, invalid zero division, overflow square and underflow square. The
[receipt](special-fp-c-review.json) binds production objects, REA, replay,
qualification and hybrid composition. Both source files now contain no assembly.
No persistent RAM or executable byte arrays are added.

Non-inlined C divide/square helpers prevent constant wrappers from discarding
runtime FP exception effects. Tail calls preserve zero additional stack depth,
matching the native single-precision leaves. The double-precision functions retain
their original Clang unit: moving them to the GCC profile would enlarge a frame.
All six double function byte sequences and relocation targets remain exactly equal
to their prior production object. The new single-precision unit uses the strict
GCC FP profile. Every stock function still has one implementation.

The production objects pass **133,458 native/C pairs**: **119,616 single-precision**
and **13,842 double-precision** regression cases. Checks cover raw result bits,
FPSCR, preserved integer/FP registers, software-double call arguments and exact
eight-byte provider depths, external writes and restored SP. The single-precision
private arithmetic helpers execute at depth zero. Inputs include raw random words,
NaN payloads, subnormals, signed zeros, all rounding directions, flush/default-NaN
modes and preexisting exception flags. Independent checks assert constant-helper
results and divide/invalid/overflow/underflow flags. Seven compiled defects are
rejected, including replacing exceptional operations with constant results.

Each C cosine, sine and tangent caller passes **87,710 cases** with the production
special helpers linked. The actual optical caller passes **1,344 gap/reset/warmup
cases** with the current C processing/math graph. The heavy optical estimator and
previously documented trigonometric frame differences remain outside this proof.

Qualification accepts the complete six-byte `r1_math_self_add32` and
`r1_math_add32` bodies: each emits the stock VADD and return bytes. Their manual
frontier sizes are now pinned to the observed two-instruction extents; REA also
reports self-add as a shared noncontiguous tail. Only these **12 qualified bytes**
were appended to the canonical source plan; every prior selection is retained.
The remaining four special wrappers have different instruction layout and are
not claimed byte-identical.

The normal build compiles **695 units**, with no failures or duplicate strong
symbols and unchanged **179 application / 34 bootloader imports**. All **693 prior
units** outside the split original module retain source/object hashes. The hybrid
application still equals locked stock. Its composition is now **4,381 source-built
executable bytes**, **641,779 stock executable bytes** and **248 resource bytes**.
That local instruction-identity improvement does not establish a complete source-only
link, whole-firmware C reconstruction or physical hardware validation.
