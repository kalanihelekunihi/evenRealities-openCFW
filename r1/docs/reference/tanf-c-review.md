# R1 tangent arithmetic and conversion in C

`native_tanf.c` now expresses seven former assembly helpers in C: add, subtract,
multiply, divide, non-fused multiply-add/subtract and signed integer conversion.
The [receipt](tanf-c-review.json) binds production source/object, REA, direct/caller
replay, defect controls and qualification. No persistent RAM or executable byte
arrays are added. The strict GCC FP profile and fixed-argument non-inlined helpers
retain operand and rounding behavior.

The conversion uses the same finite moderate-range/bias bound as
[cosine](cosf-c-review.md). Input magnitude is below 2^14, scale below one and bias
2^23; the reduced intermediate remains below 2^15 even with directed rounding.
The signed cast is representable and emits the stock truncating conversion,
followed by defined modulo conversion to uint32_t. Replay observes 59,150
conversion calls, with values in [-8192,8192]; this sample supplements the bound.

REA reports two body ranges: `0x3b048..0x3b189` for the main routine and
`0x3bad4..0x3badd` for the shared invalid-result tail. The latter retains its
existing separate helper ownership rather than being duplicated here. The small
finite path retains classifier/subnormal constant-square behavior; odd quadrants
retain the stock negative reciprocal and its FP exception flags.

The production object passes **87,710 native/C cases**, comparing raw results,
FPSCR, errno, logical helper arguments, external writes and preserved registers.
Tiny inputs also have independent identity and classifier/underflow-call checks.
Another **3,234 cases** model reducer results and caller-saved clobbers, including
NaNs, infinities, subnormals, raw quadrants and signed zero. The modeled pole cases
independently assert signed infinity and the divide-by-zero flag. Nine compiled
defects are rejected, including pole sign, missing underflow raising, wrong class,
fused math, wrong conversion, threshold and reducer-result errors.

All three C trigonometric functions execute through the C bandpass generator in
**1,108 cases**. The native optical caller passes **1,344 gap/reset/warmup cases**
with C processing helpers and C cosine/sine/tangent. The heavy optical estimator
remains outside this caller replay.

Native tangent owns sixteen bytes; this C profile owns twenty-four. Reducer output
pointers lie sixteen versus twenty bytes below entry. Native error helpers tail-call
after restoring the frame; C retains its twenty-four bytes. Classifier and underflow
calls similarly occur at sixteen versus twenty-four bytes below entry. These
differences are recorded explicitly, with private frame bytes excluded. Physical
hardware behavior remains unverified. Remaining math helpers still contain assembly.

The build remains **694 compiled units**, without failures or duplicate strong
symbols, with **179 application / 34 bootloader imports**. All **693 other units**
retain source/object hashes. The selected 56-byte tangent constant table remains
unchanged; scoped qualification selects no executable replacement. Canonical
compilation and hybrid equality still pass with 4,369 source-built executable
bytes, 641,791 stock executable bytes and 248 resource bytes. This does not prove
a complete source-only link or executable byte identity.
