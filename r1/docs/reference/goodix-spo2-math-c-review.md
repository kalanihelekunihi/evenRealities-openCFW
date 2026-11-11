# SpO2 calibration polynomial in C

The [SpO2 calculation control-flow review](goodix-spo2-calculate-c-review.md) adds native core control in C, including allocation/status flow and calibration semantics. Fourteen deeper processing stages remain explicit imports; this does not complete the SpO2 engine.

`native_spo2_math.c` implements the94-byte native calibration polynomial at0x7412c. It converts five signed integer coefficients from descriptor offsets8..24, preserves float32 polynomial operation order and divides by10000. Native nonfused multiply-adds are matched by separate C multiplication/addition. No state or imports are added.

**4,640 stock-versus-C pairs pass**, covering all94 native instruction bytes, all four rounding modes, sticky flags, default-NaN/flush-to-zero settings, finite extremes, signed zero, subnormals, infinities and signaling/quiet NaNs. Output and full active FPSCR match. Saved registers, stack and all RAM are preserved. Four compiled defects in scale, coefficient, degree and sign are rejected. The source cannot enter stock code.

The tested object equals the normal build object. All **900 R1 units** compile and compose without failures or duplicate strong symbols;889 prior nongenerated source/object pairs and source-plan/cache files are unchanged. Imports remain78 application/22 bootloader.

The core at0x6e838 and its other14 processing dependencies remain unfinished. This helper has not yet been verified through a C core caller. The existing portable model is separate. Emulator sampling with a primed FPU does not establish exhaustive input behavior, physical FPU startup or bootable firmware.

[Machine-readable evidence](goodix-spo2-math-c-review.json) pins the source, object, REA dossier and fixtures.
