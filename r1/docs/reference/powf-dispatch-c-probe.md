# C replacements for powf dispatcher assembly helpers

At the probe checkpoint, 25,728 exact stock/C comparisons passed across two compiler profiles. Six compiled defects were detected. All 1,524 stock instruction bytes/453 starts executed; REA authenticated each code range. Four private assembly helpers were replaced in the candidate. The [mainline review](powf-dispatch-mainline-c-review.md) records its subsequent promotion.

Replace only four private inline-assembly helpers:VABS/VNEG become raw sign-mask/XOR operations;VMUL becomes a noinline volatile binary32 C multiply;VCMPE-zero/VMRS becomes integer classification plus Arm FPSCR compiler builtins. Preserve FZ input-denormal status,signaling unordered behavior,NZCV and existing FP control/exception flags. No instruction-byte array or trap replaces the assembly.

All dispatcher source outside the helper block is byte-for-byte identical to the saved baseline C source,including existing branch logic,errno policy and constant declarations. Actual latest C reduced powf,classifier,math and errno dependencies are linked from the947-unit normal build;other math units still contain assembly and are outside this change.

21,504 comparisons cover the special-value cross product in all32 FP configurations plus random samples in6 modes. The actual normal r1-application-1 compiler profile adds4,224 comparisons with a two-mode cross product and six-mode random samples. Six compiled controls detect incorrect sign operations,subnormal scaling,zero flags,IDC loss and FP control-bit loss.

This probe was not itself a manifest unit. Its exact source was later promoted to `native_powf_dispatch.c` and rebuilt in the normal R1 source tree. Source-plan selections are unchanged; byte identity is not claimed.

Scalar result,full FPSCR,saved core/FP ABI,SP,masks and public RAM excluding8192 private stack bytes are compared. Caller scratch/APSR,physical hardware,timing and interrupt/concurrency behavior remain unverified. Full native dispatcher instruction coverage is measured;this is not whole-firmware boot proof.

Filter coefficient construction and lifecycle engine integration remain open.

[Machine-readable evidence](powf-dispatch-c-probe.json).
