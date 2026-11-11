# Confidence dependencies and Gaussian C probe

The ignored Gaussian candidate at `build/goal-r1-spo2-confidence-dependencies-c/candidate.c` implements native `0x3e6c8`. It is not a source-manifest unit. Confidence parent `0x95828` is still open.

REA/assembly establishes five hard-float parameters (lower, upper, mean, sigma, step) and a float return inS0; the decompiler's three-argument/core-return presentation is incomplete. The routine starts at lower+step, computes sqrt(2*pi)*sigma and its reciprocal before the zero-sigma exit, then integrates through the native signaling bounds. It uses DOUBLE exp and ordered software-double multiply/add/narrow operations, with f32 position/accumulator steps. Zero sigma still sets division status; no generic expf substitution or normalization is used.

6,656 exact stock/C comparisons pass across6,400 broad/special-value cases and256 independent numerical-oracle cases. Broad cases cover all32 FP configurations. The independent RNE oracle uses explicit f32 rounding and Python exp/sqrt with tolerance2e-6; both stock and C also match exactly. All216 native instruction bytes/57 starts execute, plus8 authenticated literal bytes. Eight compiled defects are detected, including expf substitution, endpoint/order/scale errors, zero-sigma division removal and quiet-NaN status.

Actual reconstructed C sqrtf, double exp, software binary64 arithmetic/promote/narrow and memory providers are used. Source has no stock executable mapping. S0/full FPSCR, saved GP/FP registers, SP/masks and public RAM match, excluding8192 private stack bytes and caller scratch/APSR.

Confidence also calls native dual-window extraction `0x29144` (520 bytes), mean `0x61f94`, standard-deviation wrapper `0x61fd4`, last-window `0x66394`, incremental deviation `0x66430` and count `0x66490`. Their REA dossiers/callee graphs are saved beside the probe. The extractor's peak/feature and packed-half helpers and deeper statistics must be checked before replacing the parent; historical portable routines have different interfaces and are not native providers.

Before admission: create the shared native Gaussian/support interface, verify normal objects and caller wiring, and reconstruct the remaining dependencies. Valid advancing loop configurations are assumed. Stock can loop indefinitely for nonadvancing inputs; an initial negative-infinity-step run hit the native instruction budget. The candidate retains native behavior and adds no loop cap. Physical hardware, timing, interrupts/concurrency and trap behavior remain unverified.

[Probe evidence](goodix-spo2-confidence-dependencies-c-probe.json).
