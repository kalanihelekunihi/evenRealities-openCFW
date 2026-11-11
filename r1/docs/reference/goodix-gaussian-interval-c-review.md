# Native Gaussian interval in C

`native_gaussian_interval.c/.h` implements native `0x3e6c8` with no assembly or writable global state.

Assembly establishes five hard-float arguments lower/upper/mean/sigma/step and scalar S0 return. The decompiler three-argument/core-return presentation is incomplete. This native C interface is distinct from historical portable guessed APIs. The right-endpoint integration begins at lower+step and keeps that first position as the native lower-loop guard.

Compute sqrt(2*pi)*sigma, signal-compare sigma against zero, then divide1 by the normalization denominator BEFORE the zero-sigma exit. This preserves division flags even when the returned integral iszero. Loop comparisons preserve VCMPE carry/zero/unordered and FZ effects; positive advancing steps include the native upper endpoint. No generic input normalization or loop bound is invented.

Position/exponent arithmetic and each accumulator step use separately rounded f32 operations. The exponential itself is DOUBLE exp. Actual C soft binary64 promotion,multiply,multiply,add and narrowing preserve native arithmetic order; expf substitution is demonstrably different. Source uses actual reconstructed C sqrtf/exp/math providers with no stock executable mapping.

REA authenticates216 instruction bytes and8 literal bytes. All216 instruction bytes/57 starts execute. Eight compiled defects detect endpoint,zero-sigma division,normalization,sigma-square,step-direction,quiet-NaN-status and expf substitution errors. Independent Python f32-rounded sqrt/exp rectangle oracles run under RNE with tolerance2e-6; exact stock/C comparisons remain separate evidence.

8,112 exact stock/C comparisons pass,including512 with independent numerical oracles. Eight compiled defects are detected. All939 normal units compile without failures or duplicate strong symbols. All928 prior source/object pairs are unchanged. Normal sections and decoded symbols equal the tested candidate after source-file symbol normalization. Imports remain63 application/22 boot.

Tests cover positive advancing steps and explicitly safe early exits, zero/negative/nonfinite sigma and special payloads. Native nonadvancing configurations can fail to terminate,including negative-infinity step with an eligible upper bound; an initial native probe hit its instruction budget for that input. That invalid loop configuration is excluded rather than patched with a loop cap.

Comparisons check S0,full FPSCR,public RAM excluding8192 private stack bytes below SP,savedR4-R11/S16-S31,SP and interrupt masks. Candidate broad tests cover32 FP configurations; normal broad samples use six and independent numerical oracles RNE. Caller scratch/APSR,trap behavior,timing,interrupts/concurrency and physical hardware are unverified.

The normal939-unit build remains relocatable composition with63 application and22 boot imports,not a complete bootable firmware. No import is removed yet because confidence is not integrated. The confidence parent,dual-window feature extractor and statistics dependencies remain open; other hardware/startup work remains. Source plan and health-cache layout are unchanged.

[Machine-readable evidence](goodix-gaussian-interval-c-review.json).
