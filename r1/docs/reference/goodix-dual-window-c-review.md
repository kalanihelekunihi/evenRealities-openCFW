# Native dual-window features in C

`native_dual_window_features.c/.h` implements native29144 without assembly or owned writable state. 584 exact stock/C comparisons pass,including28 bounded correlation-oracle checks. Eight compiled defects are detected. All520 instruction bytes/181 starts execute;REA authenticates code and8 literal bytes.

Eight core arguments: channel record,RMS0,RMS1,correlation,rate0,rate1,quality0,quality1. Read live history pointer/count pairs at216/220 and232/236;each supplies its last125 binary32 samples. Actual C heap and full native C helpers perform normalized autocorrelation,37-row peak selection,metric sentinel mutation and rate extraction. No helper is replaced by a fixed-output boundary.

Keep allocation sizes500/126/252/250 and native lifetime/order. No-peak branches write only RMS0.5;rate and quality outputs retain previous contents. Cache input/output arguments while loading second history only after first-channel metrics,rate and packing.

First-channel energy is measured before custom5/10 packing. The second channel reuses the workspace. Unpack packed first-channel values through the S0 ABI and accumulate sample-first products with separately rounded VMLA semantics. Signaling less-than/unordered root gates clamp negative/NaN energies to0;ordered equality gates short-circuit zero-energy correlation. Divide by the product of unquantized-channel energy roots,then free actual heap objects.

Probe only;candidate is not admitted to the source manifest. Histories125/160 with valid mapped/aligned buffers are tested. History count below125,invalid owner-pointer aliases and allocation failure recovery are not assigned invented behavior.

Public RAM excludes8192 private stack bytes below SP. Full FPSCR,saved R4-R11/S16-S31,SP and interrupt masks are checked. Void caller scratch/APSR and incidental restored R0/R1 are excluded;the C interface returns no value. Physical hardware,timing and interrupts/concurrency remain unverified.

28 independent finite-input correlation oracle checks use fsum and bounded IEEE-half packing approximation with absolute tolerance0.001 in nearest mode;they do not independently prove every feature output. Exact stock/C comparisons check all public RAM/FPSCR. The original broad probe uses6 FP modes and edges32;normal broad/edges use2.

All946 normal units compile without new imports or duplicate strong symbols;935 prior source/object pairs are unchanged. Normal provider matches candidate sections and decoded symbols after source-file symbol normalization. This remains relocatable composition with63 application and22 boot imports,not complete bootable firmware. Confidence and hardware/startup dependencies remain open.

[Machine-readable evidence](goodix-dual-window-c-review.json).
