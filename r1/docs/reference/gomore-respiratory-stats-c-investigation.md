# Respiratory statistics C investigation

This is the pre-integration checkpoint. The subsequent [C review](gomore-respiratory-stats-c-review.md) records consolidation and production-object replay.

Three experimental C providers compile under strict GCC settings without assembly:
encoded count `0x967a0` (36 bytes), descending argmax `0x760ec` (46 bytes), and
thresholded five-sample mean `0x76120` (84 bytes). The
[receipt](gomore-respiratory-stats-c-investigation.json) binds REA bytes/pseudocode,
source/object, disassembly and replay under the ignored build directory.
Production and its source manifest are unchanged at this checkpoint.

Encoded counting reads raw words and tests the inclusive wrapped interval
`(word+0xbf200000)<=0xe80000`, with a signed loop bound. Argmax starts at index
length-1 with positive-zero maximum, scans backwards and updates only for a
strictly greater sample. Ties therefore preserve the later index. Counts zero
and minus one return raw index words without data reads in the tested matrix.

Thresholded mean takes threshold in S0, sample pointer in R0, comparison pointer
in R1 and destination in R2. It writes output zero before reading comparisons,
reads each weight before deciding whether to load that sample, reloads the
accumulator before each addition and divides by the included count even when
zero. Output aliasing into samples/weights changes later reads. Signaling
VCMPE comparisons and ordered VADD operands are emitted by non-inlined C helpers.
This avoids the generic helper's local-sum alias behavior and null guards.

**3,583 native/C cases** pass across selected raw FP patterns, NaNs/infinities,
signed zeros/subnormals, four rounding modes, default-NaN/flush-to-zero and five
output locations. Full memory, raw result, FPSCR, final SP and saved integer/high
FP registers agree. **768 count/argmax cases** additionally check independent
return expectations, including flush-to-zero comparison behavior. **Fifteen
finite threshold cases** check an independent ordered byte/arithmetic model with
aliased destinations. The independent model does not claim full FP-flag coverage;
flags are compared directly against stock.

Seven independently compiled defective variants are rejected: exclusive encoded
upper bound, argmax tie/default changes, strict threshold, skipping zero-count
division, swapped addition operands and four-sample loop bound. Compilation
failures do not count. **102 boundary cases**, including 76 faults, agree on
invalid access address/size, partial writes, return, memory and FPSCR. Private
stack writes are excluded; huge/wrapping loop bounds and physical alignment
remain unproven.

The actual native respiratory routine passes **840 paired executions** with the
three statistics functions native versus replaced by C. Encoded counting is
reached 840 times; argmax and thresholded mean are reached 560 times each.
The optical estimator is modeled; native software math, history and clearing
execute normally. Coverage includes elapsed/initial-counter values, rate and
confidence boundaries/special values, unavailable flags, aliased output and FP
modes. Full record/output, result, estimator arguments, helper call sequence,
FPSCR, final SP and saved registers agree. This is C-helper caller integration,
not a reconstructed native respiratory root or optical estimator.

Production owner consolidation and normal-build promotion remain pending. Existing generic owners
have checked signatures and different alias/guard behavior; consolidate those
explicitly before production promotion. The full respiratory update and optical
period estimator remain unresolved, as do physical execution, final source-only
linking and byte identity. The normal build remains 686 units with 179 application
and 34 bootloader unresolved imports.
