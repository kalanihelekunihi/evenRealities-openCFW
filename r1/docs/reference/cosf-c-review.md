# R1 cosine arithmetic and conversion in C

`native_cosf.c` now expresses all seven former assembly helpers in C: add,
subtract, multiply, non-fused multiply-add/subtract, negate and integer conversion.
The [receipt](cosf-c-review.json) binds source/object, REA, replay, defect controls,
data selection and qualification. No persistent RAM or executable byte arrays are
added. Existing range reduction, polynomial constants and external helper bindings
remain. Normal compilation uses GCC 9 with strict FP flags and fixed-argument,
non-inlined arithmetic helpers to retain operand and rounding behavior.

The float-to-int cast is defined at its only call site. The raw input guard
restricts this path to finite magnitudes below `0x46490e49`, hence below 2^14.
The scale `0x3f22f983` is positive and below one; the bias `0x4b000000` is 2^23.
Even allowing directed rounding at the bias operation, the reduced intermediate
has magnitude below 2^15. It is finite and representable as int32_t. Casting that
signed result to uint32_t gives defined modulo conversion for negative quadrants.
The compiler emits the stock truncating `VCVT.S32.F32`. The replay observes 59,122
conversion calls, all within [-8192,8192]; that sample supplements the guard-based
bound rather than proving every possible input by enumeration.

The production object passes **87,710 native/C pairs**, checking raw FP results,
FPSCR, errno, logical helper arguments, external writes and preserved registers.
Inputs cover raw random words, moderate-range samples, threshold neighborhoods,
special values and seven FP control settings. Another **3,234 cases** model the
reducer with clobbers, raw quadrants and NaN/inf/subnormal reductions. Seven
compiled defects are rejected, including fused math, unsigned conversion,
polynomial sign, threshold and reducer-result errors.

The real C low/high-pass and bandpass callers pass **1,376** and **1,108** cases
with this production cosine object and native remaining math. The native optical
caller passes **1,344 gap/reset/warmup cases** with existing C processing helpers
and this cosine. Heavy optical estimation remains outside that caller replay.

Stack identity remains open: native cosine owns eight bytes; this C profile owns
sixteen. The reducer's output pointer lies eight versus twelve bytes below entry.
Native error-helper tail calls restore the entry stack; C retains its sixteen-byte
frame for those calls. These differences are recorded, not normalized into an
identity claim. Private frame bytes are excluded. Remaining math dependencies
still contain assembly; no physical hardware validation is claimed.

The build still compiles **694 units** with no failures or duplicate strong
symbols and **179 application / 34 bootloader imports**. All **693 other units**
retain source/object hashes. The canonical plan selects only cosine's 56-byte
constant table; its bytes/hash are unchanged. Scoped executable qualification
selects no new region. Canonical compilation and hybrid output still pass, with
4,369 source-built executable bytes, 641,791 stock executable bytes and 248 resource
bytes. This does not prove a complete source-only link or executable byte identity.
