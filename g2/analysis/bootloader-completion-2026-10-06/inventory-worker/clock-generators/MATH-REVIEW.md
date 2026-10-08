# PLL math continuation — source review only

During SybilSight ingestion hold, added `clock_pll_math.c` and `clock_pll_rounding.c`. **Neither has been compiled or executed.** The 688 PASS receipt applies only to `clock_generators.c`; it does not validate these drafts. Existing checkpoint and receipts are unchanged.

Stock floating-register ABI uses s0/s1 for floats and r0/r1/r2 for pointer arguments; explicit `pcs("aapcs-vfp")` declarations retain this despite the project's softfp build convention. Verify ABI on compilation before linking.

Recovered function contracts:

| Body | Draft behavior | Unresolved dependency |
|---|---|---|
| 426d48..426db2 | float GCD, swap if first<second, stop at second<2^-23, max16 floor/remainder iterations, return -1 on exhaustion | floor; instruction-level FP validation |
| 426db4..426eac | integer mode, derive target/GCD and reference/GCD; reject noninteger remainder>epsilon, rounded multiplier>960, divider>63; normalize multiplier to minimum4, validate divider1..63 and multiplier4..960 | GCD, fmod, round |
| 426eac..426f6a | fraction mode: ratio=target/reference; divider=ceil(10/ratio), feedback=ratio*divider; round fractional part*2^24; floor integer part; accept divider<=63 and integer10..96 | ceil, fmod, round, floor |
| 426f6c..427032 | NULL returns6; VCO outside60..960MHz returns5; integer first, fraction fallback; failure1; success writes descriptor1/2/3/6/8 only; high mode>=240MHz | integer/fraction children |
| 427c90 +427ca0 | bitwise floor; retain signedzero, values already integral at large exponent, infinities and NaN bitpatterns | standalone comparison pending |
| 427d98 +427da8 | bitwise round nearest/ties away, signedzero below0.5, +/-1 for0.5..1 | standalone comparison pending |
| 427dd0 +427de0 | bitwise ceil; negative small nonzero→negativezero, positive small nonzero→1 | standalone comparison pending |

Stock literal limits are epsilon `0x34000000`, epsilon-next `0x34000001`, 960-next `0x44700001`, 63-next `0x427c0001`, 96-next `0x42c00001`. Integer/fraction/VCO compares use next-float bounds to implement inclusive maxima and strictly-greater epsilon rejection. Draft comparisons reflect those thresholds; unordered/NaN branch behavior and FPSCR effects still need original-instruction comparison. GCD explicitly emits original nonfused VMLS; compile other float arithmetic with `-ffp-contract=off`.

fmod at427ccc wraps integer body427cdc..427d98. It has normal and subnormal remainder paths, exceptional-value canonicalization, and a conditional tail into4275c4 (domain-error store33). Generic host `math.fmod` is not proven to retain these behaviors. This is the next concrete source/validation boundary, not a reason to expand scheduler inventory.

Deferred tests after ingestion release: rounding raw bitpatterns around +/-0, +/-0.5, integer transitions, exponent23/24, infinity, qNaN/sNaN; GCD16-iteration/exhaustion and FP remainder; integer multiplier4/960 and divider1/63 boundaries; fraction integer10/96 and fractional carry; VCO NULL,60/240/960 boundaries and retained descriptor bytes; fmod signs, exact multiples, exponent gaps, subnormals, NaN/Inf/zero and domain side effects. Execute original instructions rather than accepting SDK text or host libm as the oracle. Re-run existing688 cases with native math descendants only after the lower bodies are recovered. Seven integration cases remain deferred and current e1049dc3 remains authoritative.
