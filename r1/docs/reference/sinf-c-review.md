# R1 sine arithmetic and conversion in C

`native_sinf.c` now expresses its seven former assembly helpers in C: add,
subtract, multiply, non-fused multiply-add/subtract, negate and integer conversion.
The [receipt](sinf-c-review.json) binds production source/object, REA instructions,
replay, controls, data selection and qualification. No persistent RAM or executable
byte arrays are added. Compilation uses the strict GCC FP profile and fixed-argument,
non-inlined helpers to preserve operand order.

The signed integer cast has the same finite moderate-range guard and bias reduction
as [cosine](cosf-c-review.md): input magnitude below 2^14, scale below one, bias 2^23,
and a reduced intermediate below 2^15 even with directed rounding. The cast is
representable and emits the stock truncating conversion; conversion to uint32_t
then preserves negative quadrant bits with defined modulo behavior.

REA confirms sine's small finite path calls the integer classifier, and class four
(subnormal) invokes the stock constant-square helper. That helper loads 0x10000000
and squares it; it does not consume an FP argument. The returned square is ignored
and the original input is returned, including its zero/subnormal sign and bits.
The classifier and underflow helper remain separate modules with assembly.

The production object passes **87,710 native/C cases**, comparing raw results,
FPSCR, errno, logical provider arguments, external writes and preserved registers.
The tiny-input path also has independent input-identity and exact classifier/
underflow call expectations. A further **3,234 cases** model reducer output and
caller-saved clobbers, including raw quadrants, NaNs, infinities and subnormals.
Nine compiled defects are rejected, including omitted underflow raising and wrong
classifier tags, as well as fused math, wrong integer conversion and polynomial signs.

Both C cosine and sine now execute through the C low/high-pass and bandpass callers:
**1,376** and **1,108 cases** pass, including their existing fault cases. The native
optical caller passes **1,344 gap/reset/warmup cases** with both C trigonometric
functions and the existing C processing helpers. The heavy optical estimator path
remains outside this caller replay.

Stack identity remains open: native sine owns sixteen bytes; this C profile owns
twenty-four. Reducer output pointers lie sixteen versus twenty bytes below entry.
Native error helpers tail-call after frame restoration; C retains its twenty-four
bytes. Classifier and underflow calls similarly occur at sixteen versus twenty-four
bytes below entry. These differences are recorded explicitly; private frame bytes
are excluded. Physical hardware behavior remains unverified.

The build remains **694 compiled units**, with no failures or duplicate strong
symbols and **179 application / 34 bootloader imports**. All **693 other units**
retain source/object hashes. The selected 56-byte sine constant table is unchanged;
scoped qualification selects no executable replacement. Canonical compilation and
hybrid equality still pass with 4,369 source-built executable bytes, 641,791 stock
executable bytes and 248 resource bytes. This is not a complete source-only link
or executable byte identity proof. Remaining math dependencies still contain assembly.
