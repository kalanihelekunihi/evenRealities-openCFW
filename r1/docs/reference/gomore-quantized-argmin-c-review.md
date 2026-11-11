# R1 quantized valley selector in C

`native_gomore_quantized_argmin.c` supplies `0x4ec9c`, a dependency of the
optical peak matcher. REA confirms an unsigned reversed-range guard, an initial
read and integer conversion even for equal bounds, then a signed-word exclusive
loop. Each iteration converts the current integer threshold to float before
reading the sample; only an ordered smaller sample updates the integer minimum.
For example, samples 1.9 then 1.1 retain index zero because the first threshold
is quantized to one. The generic guarded utility retains its behavior under
`gomore_primitives_quantized_argmin_checked`.

The C casts stay within the signed integer range. Integer classification handles
NaNs and overflow: zero for NaNs, signed saturation for infinities/overflow, and
`r1_math_invalid32` supplies IOC through C zero division. This avoids undefined
out-of-range casts while retaining native flags. Finite in-range conversion uses
VCVT emitted from C. No inline assembly or persistent RAM is added.

The production object passes **5,744 result/FP-state comparisons and three fault
comparisons**. Cases cover raw random values, both NaN types/signs, infinity,
conversion boundaries, subnormal inputs, signed zeros, signed/wrapped bounds,
equal bounds, and seven rounding/FZ/DN settings. The comparisons include return
index, buffer writes, complete FPSCR, return completion, SP and callee-saved
registers. Six compiled defects are rejected: floating threshold, inclusive end,
skipped first iteration, missing invalid operation, wrong NaN result and wrong
saturation. The fault cases confirm the first invalid sample access and FP state;
they are not a complete bus-fault or alignment model.

**56 native peak-matcher caller pairs** pass with C statistics and this selector:
126 valley calls, 112 mean calls, 112 median calls, 56 deviation calls and 616
comparator calls on each side. All externally visible memory writes, state,
return and FPSCR agree. This fixture does not exercise subrange sorting. A
separate **112 native optical-root pairs** exercise 208 C subrange-sort calls,
304 mean, 112 median, 152 deviation and 512 comparator calls; they make zero
valley calls. Qsort, power, square root, the peak matcher and optical root remain
stock executable code in these caller fixtures. Private stack writes are excluded.
The direct selector fixture uses the stock invalid-operation helper; caller
fixtures link the already-reviewed C special-value provider.

Native selector frame is eight bytes. C uses a 16-byte outer frame plus helper
frames (quantize adds eight bytes), and overflow/NaN paths call the invalid helper.
Private layout and instruction identity differ. Qualification selects zero
regions; the canonical source plan is unchanged.

The normal source build passes **699 units: 625 application and 74 bootloader**,
with no failures or duplicate strong symbols. Imports remain 179 application and
34 bootloader. Hybrid equality passes with 4,381 source-built executable bytes,
641,779 stock executable bytes and 248 resource bytes. Full C linking, the C peak
matcher/root, whole executable byte identity and physical hardware validation
remain open. The [receipt](gomore-quantized-argmin-c-review.json) binds evidence.
