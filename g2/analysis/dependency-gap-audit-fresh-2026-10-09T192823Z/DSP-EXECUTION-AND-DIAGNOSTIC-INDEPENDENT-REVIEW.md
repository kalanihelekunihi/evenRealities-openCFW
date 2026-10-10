# Independent DSP execution and packed-negation diagnostic review

**PASS for artifact/accounting verification, not universal equivalence.** [Execution receipt](DSP-EXECUTION-INDEPENDENT-VERIFICATION.json) passes36 checks; [diagnostic receipt](DSP-NEGATION-DIAGNOSTIC-INDEPENDENT-VERIFICATION.json) passes25 checks. No build or guest replay was performed by this audit.

## Accounting that must remain separate

| Evidence cohort | Observed result |
|---|---|
| Authentic C versus assembly helpers |230 passes|
| Authentic C versus assembly bitreversal |3 passes; no separate executed permutation oracle|
| Authentic C versus assembly FFT |23 passes,1 failure,32 unrun|
| Original289-case corpus |256 passes,1 failure,32 unrun|
| Separate packed-negation diagnostic FFT |33 passes: original failing vector plus32 formerly unrun positions|
| Separate abs-max assembly oracle |55 passes|
| Extreme MAC documented-operation/model probes |6 discrepancies, not passes;2 z0 observations repeat predecessor probes|

Thus every planned FFT vector position has now been observed under some implementation, but there is neither a56-case authentic-C pass nor a56-case diagnostic pass. The earlier23 positions were not replayed under the diagnostic. Original failure remains immutable.

Actual abs-max55 is five lengths0/1/3/4/512 times11 cyclic edge rotations, not the prior proposed nine nonzero lengths times six patterns plus zero. Actual ramp begins0 rather than-32768 and full-range LCG reinterprets the high16 as signed rather than subtracting32768; these are recorded fixture variants. The constant32767 failing vector itself is unchanged. Smoke and stage probes are not extra corpus passes.

## Harness and ABI review

Six retained executable hashes/segments/entries and raw memlogs agree with receipts; built QEMU binary hash matches its recorded identity. All executable load regions lie in smartl RAM0 at10000, with explicit stack20010000 in RAM1. The library’s former10003000 placement is no longer used as code;10003000 and10002000 are the declared memlog/exit MMIO devices. QEMU ELF loading preserves each segment’s file/memory-size contract, including zero-fill BSS; the corpus explicitly resets buffers, guards, random state and counters. Source descriptors select complex256/real512, bitreverse1, modifier1. Three generated tables and their linked executable bytes match the authenticated locked tables and are4-byte aligned. Renamed assembly objects preserve all nine previously authenticated text sections/1,606bytes.

Assembly split receives its fifth modifier argument through the ABI stack slot after saving l0; helper and wrapper pointer/length fields have fixed32-bit target layouts. Shared dispatch/RFFT wrappers are authentic compiled C on both sides, with separately bound kernel namespaces. These tests isolate selected stock-byte kernels; they are not execution of the entire original firmware RFFT wrapper or a GX8002 platform model.

Two guard limitations remain: compare returns immediately on the first output mismatch, before checking outer canaries, so the original failing case’s guard state is not logged. Successful helper cases compare the entire capacity and outer canaries, but lack an independent unchanged-tail oracle at the logical length; equal unintended writes by both implementations could evade that check. The separate abs-max oracle checks its output tail but not every input/outer canary. Stage arrays lack outer canaries. These limits do not erase the directed opcode/source distinction, but prevent overstating memory-safety validation. A future generated harness should check canaries before difference reporting and independently check untouched logical tails.

## Localized distinction and manual boundary

Original unsigned log values44668/44670 decode to-20868/-20866. Case256 minus233 helper/bitrev passes gives FFT ordinal23, pattern5/inverse/real512. The first original full-pipeline difference is at index1. A conjugate-mirrored spectrum with DC/Nyquist imaginary zero reproduces a split-stage index1 difference C0 versus assembly1. The fixture is valid as a Hermitian real-spectrum shape; it is not a captured physical spectrum. Seven power-of-two prefixes512..8 are bounded diagnostics, not proof of a globally minimal counterexample.

The retained E804 manual’s original ASCII equations confirm independent saturated signed16 lane negation. Product1fffc000 has lanes8191/-16384, hence packed-neg e0014000 versus scalar32-neg e0004000. Adding1fffc000 yields10000 versus0, explaining emitted split halfwords1 versus0. Actual opcode and stage logs agree. This documented/source/model finding supports a distinction in the selected stock assembly operation; it certifies neither physical GX8002 execution nor the correctness of an audio algorithm.

The same manual saturates the entire MAC accumulator-plus-two-products expression. For x=y80008000, product sum is2147483648. Documented results for z0,-1,INT32_MIN are7fffffff,7fffffff,0. The pinned QEMU helper narrows the product sum before saturated addition and observed outputs are80000000 for both MAC instructions at all three accumulators. A pre-saturated product-sum workaround would also be wrong for cancellation; no simulator patch or normalization is warranted by this audit.

The coefficient check correctly excludes only that singular all-minimum-pair intermediate-overflow corner from three selected real-split ADD-MAC sites. All256 locked A pairs differ from80008000; derived B’s saturated-absolute low lane is at most32767, so B also cannot equal it. Each recorded site multiplies by A or B. This proof applies to real512/modifier1 and the named assembly sites, not all compiled C arithmetic, other lengths/tables, physical instructions or the simulator generally.

## New diagnostic review

Undoing the helper insertion, diagnostic export names and the one declared little-endian inverse-negation expression recovers the original file byte-for-byte. Original source hash remains valid. The helper sign-decodes16-bit patterns into bounded int32_t values, saturates minimum negative, and packs masked uint32_t lanes. Independent formula checking covers all65,536 single-lane encodings; it is a mathematical review, not host firmware execution. No signed overflow/negative shift occurs in this helper. Other original C arithmetic remains untouched and has no new universal portability claim.

The diagnostic run skips exactly FFT positions0..22, starts its independent count at256, and reports33 comparisons. Vector generation/call/comparison bodies are unchanged. Wrapper text is unchanged during inverse-symbol redirection; compiled authentic functions and the assembly side remain present. The stage diagnostic removes the differences for the three fixture modes and seven prefixes. This is finite evidence that the single negation distinction explains the tested discrepancy, without admitting the diagnostic as authentic source or canonical fidelity.

## Next finite discriminator

[Plan](NEXT-INVERSE-SPLIT-DISCRIMINATOR.json) specifies twelve endpoint-valid spectra with only DC and Nyquist real bins equal to a selected amplitude. Test original C, diagnostic C and exact assembly at the split stage, with canaries checked first. With the locked first coefficient pair, original split imaginary0 is expected; documented packed arithmetic predicts1 for odd amplitudes and0 for even amplitudes. Residue2 modulo4 has an internal65535 accumulator difference hidden by the final high16 extraction. These vectors avoid the separate all-minimum MAC corner and test carry/borrow localization more directly than arbitrary prefix reductions. Predictions are analytical and not newly executed. Do not resume broader sweeps solely to turn a mixed-cohort count into a larger pass total.

Source availability, C compile/link completeness, finite numerical behavior, whole-payload completeness and locked-bundle equality remain distinct. No canonical coverage percentage changes. No source/production/Git/device/model mutation or new execution was made by this audit.
