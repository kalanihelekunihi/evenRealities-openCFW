# R1 hardware square root through a C builtin

`native_math_sqrt.c` now contains **no inline assembly**. The float helper at
stock `0x3b00e` uses `__builtin_sqrtf(x)` with Clang's `-fno-math-errno`, which
emits the hardware `VSQRT` directly. The existing explicit errno logic remains:
set the shared errno cell to 1 only when the result is NaN and the original
input was not NaN. Existing errno survives other inputs, including NaNs.
The builtin is a compiler-supported C extension; no claim of portable hardware
exception behavior across arbitrary C implementations is made.

The [receipt](sqrt-builtin-c-review.json) binds current source/object hashes,
raw-image-checked REA bytes and replay artifacts. **114,688 paired complete
stock/C helper cases** pass: 3,584 binary32 patterns cover every exponent, both
signs, selected mantissas and seeded inputs under 32 rounding/FZ/DN/sticky-flag
combinations. Existing errno alternates between zero and a nonzero sentinel.
Result bits, FPSCR, errno and its guards, preserved registers, SP and masks
match. The actual native/C errno paths execute without provider replacements.
The FPU is warmed; first-use activation, caller-clobbered registers/APSR and
private stack bytes are outside this proof.

The actual C RMSSD caller chain also passes **6,525 paired cases**, including
its two bounded nonterminating prefixes and SDK logging of mutated sample
results. Allocation/free, activity and logging remain modeled in that fixture;
C sqrt, float-bit promotion and memory helpers execute. Six compiled defects
are rejected: absolute input, omitted errno update, erroneous errno for NaN
inputs, wrong errno value, lost signed zero and returning the input.

The binary64 sqrt and errno-setter text sections, their relocation bindings,
and the errno storage section are unchanged from the previous production
object. No RAM owner or import is added. All **672 units** compile without
duplicate strong symbols; the other **671 source/object pairs** and both import
sets remain unchanged: **163 application / 34 bootloader** unresolved symbols.
The qualifier rejects the new float helper; no instruction-qualified bytes are
added. The canonical plan remains **4,369 source-built bytes**, and the fresh
hybrid matches the locked application using executable pull-through. Full
source-only linking, final whole-image errno initialization/placement, byte
identity and physical device operation remain unproven.
