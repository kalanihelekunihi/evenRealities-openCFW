# R1 accelerometer classifier root in C

`r1_gomore_accel_features_native` now implements stock `0x67e4c` in `native_gomore_accel_features.c`, using the existing shared C mean, ring, autocorrelation, crossing and classification providers. It closes the native classifier import from the preprocessing stage. The configurable checked classifier utility retains its distinct caller-supplied model/callback API; the new provider implements the fixed stock boundary.

REA's function dossier and instructions are saved in `build/goal-r1-gomore-accel-features-c/rea-root.json`. The C root preserves mean-call and output-store order; raw signed floating-point encoding thresholds for rate halving; the raw primary gate; native autocorrelation output addresses; crossing-mode output order; the otherwise discarded recent-mean call; signed count ratio; activity, score/trend and secondary gate order; cursor reloads; and raw zero return. Its C frame differs from stock. No inline assembly or executable byte arrays are added.

The classifier subset links using normal production objects without undefined symbols, native-address bindings or placeholders. The root, preprocessing stage, autocorrelation kernel/wrapper, period estimator and period helpers are defined text symbols. This is a complete source link for the tested subset, not for the entire firmware.

Production-object replay against the locked stock application passes:

- 2,304 classifier pairs across four signal shapes, three periods, eight levels around both gates, all eight ring positions and three FP environments. The C root runs 2,304 times, C autocorrelation wrapper 2,304 times, period 4,032 times, IIR 806,400 times and transition 23,520 times.
- 384 further rate-folding cases, with native branch hooks proving 24 entries at `0x67f2a` and 36 at `0x67f4e`. These cover both low-variance and low-mean rate-halving conditions. Broad earlier cases did not execute these branches; a surviving no-halving mutation exposed that gap. The final fixture includes period-20 inputs that distinguish the mutation.
- 128 asymmetric-ring cases, added to distinguish a real cursor from a hard-coded zero cursor.
- 144 cases with the output overlapping the beginning of state or its `0x204` history block.
- 48 preprocessing-stage pairs, including 12 calls through the new classifier. Final memory, ordered external writes, return, SP, preserved registers, masks and lower FPSCR bits agree in these cases.
- All three compiled defects rejected: wrong primary band threshold, omitted rate halving, and fixed cursor zero. Controls compile successfully and fail native-versus-C behavioral comparisons.

The direct classifier fixtures compare external memory, ordered external writes, raw return, SP, callee-preserved registers, masks and lower 28 FPSCR bits. They intentionally exclude nested helper traces because the C root has a different frame and publishes different private scratch addresses. They do not normalize public input/output pointers. Full FPSCR comparison flags, all possible aliases, private frame bytes, invalid-pointer faults, MMIO aliases, stack bounds, timing and physical device behavior remain unproven.

The normal build passes 720 R1 units (646 application / 74 bootloader), with no failed units or duplicate strong symbols. Application imports drop from 178 to 177 by removing exactly `r1_gomore_accel_features_native`; bootloader imports remain 34. Both source manifests pass `make sources-check`. The canonical instruction-matching source plan is unchanged. Byte identity is not a completion requirement, and no paid compiler is required for this work. No firmware was flashed, committed or published.

[The receipt](gomore-accel-features-c-review.json) records test results, normal-build hashes and source-link closure. Broader firmware reconstruction remains unfinished; this resolves the accelerometer classifier dependency rather than establishing hardware operation.
