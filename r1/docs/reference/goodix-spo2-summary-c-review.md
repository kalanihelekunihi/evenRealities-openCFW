# Native SpO2 summary graph in C

`native_spo2_summary.c` implements the dispatcher at `0x290bc` and its full
motion, auxiliary, peak-pair, pulse-statistics and correlation dependency graph.
Seventeen C ABI entries cover fifteen REA bodies and1,742 native instruction
bytes. Window-mean bodies include shared mean tail entries at `0x9293e` and
`0x9295c`; their bytes are counted once. The shared header replaces the caller's
external declaration, without changing its compiled object.

The implementation preserves live count reloads after output clearing, sample-first
float mean addition, separate VMLA/VMLS rounding, first minimum ties and unordered
FP branches. Motion clips at125 samples, retains the native variance/threshold
recomputations and unsigned conversion status, then uses defined signed RTZ
conversion. Peak pairing keeps wrapped global-to-window offsets and excludes a
minimum exactly at the next maximum. Pulse statistics retain the inclusive
0.85/1.15 fallback gates, final-minimum guard and floor5/6 readiness rule. One-sided
quartile masks clear their outlier count.

## Verification

- 38,459 direct routine comparisons cover all17 entries,32 floating-point
  configurations, special values, counts, aliases, exact tail thresholds, independent
  finite statistics, instruction coverage and16 positive defect-witness baselines.
- 84 real-constructor streams add3,264 constructor/stage snapshot comparisons:
  64 candidate streams across all32 FP settings,16 normal-product streams and
  four longer normal-product streams. The latter reach the20-entry history limit.
  Ratio, summary and quality run together through dropout and recovery.
- 108,888 paired rolling-push invocations execute actual C float/signed16 queues.
  Saved registers and SP are checked after each call. Full RAM/FPSCR comparisons
  occur at constructors and each ratio/summary/quality boundary, not at every push.
- Exact comparisons include full FPSCR, public RAM/heap outside an8,192-byte
  private stack region, saved R4-R11/S16-S31, SP and interrupt masks. Native return
  values are checked where the entry defines one. Source execution maps no stock code.
- Independent checks include203 finite primitive/motion/outlier cases and five
  tail-statistic cases. Correlation tolerance is2e-6; the tail mean/CV tolerance
  is1e-6. All retain exact stock comparisons.
- Sixteen compiled defects are rejected, including NaN operand order, skipped
  count clearing, wrong dot/squares, negative correlation, minimum ties, peak/tail
  boundary errors, readiness rounding, one-sided masks and wrong channel selection.
- All590 native instruction starts /1,742 body bytes execute. This does not imply
  exhaustive path or input coverage.

The normal build compiles and composes all918 units without failures or duplicate
strong symbols. Imports fall84 to83 application, while boot imports remain22.
906 unrelated source/object pairs and the caller object are unchanged. The normal
provider's code, relocations and decoded symbols match the tested object after
normalizing source-file metadata. Normal-product streams use a fresh archive from
the918-unit build. Source plan and health-cache linker layout remain unchanged.

[Machine-readable evidence](goodix-spo2-summary-c-review.json) records input/output
hashes, entry addresses and exact proof limits. No assembly or writable allocated
sections are added to the new unit; some existing math/ABI dependencies retain
assembly. Zero-length minimum and malformed index buffers are outside the valid
native contract. Physical sensors, interrupt concurrency and complete startup
remain untested. Six SpO2 stages remain unresolved, and the composed image is not
a complete bootable firmware image.
