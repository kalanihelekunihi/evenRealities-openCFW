# Native SpO2 confidence in C

`native_spo2_confidence.c/.h` implements native95828 and closes its existing calculate import. 1,176 stock/C comparisons pass:192 direct full graph,912 explicit feature-output boundary,and72 calculate/model/output caller pairs. Eight compiled defects are detected. All674 instruction bytes/243 starts execute;REA authenticates code and56 literal bytes.

Native95828 processes one channel record through pointer-to-record and pointer-to-state arguments. Cache both pointed-to addresses before the actual C eight-argument dual-window feature call. Blend rate estimates within distance10 using actual software-double0.8/0.2 multiply/add/truncate;select quality via signaling carry comparison. Evaluate the configuration word at28 AFTER features.

Enabled processing allocates496 bytes for timing differences,uses live timing pointer/count248/252,converts signed u16 differences to binary32,and calls the actual C124-sample mean even though its value is discarded. Float-count standard deviation drives signed raw quality/variance counters,including wrap and signed-byte mode policy.

Preserve positive-rate acceptance thresholds,empty-history bootstrap,miss-byte wrap and stale-rate hold rules. Actual C rolling-window push/mean/count/stddev feed a software-double mean*0.05 radius and the C Gaussian interval. Nonpositive rate only increments the miss byte. Record state fields are accessed in native order.

Direct full-graph comparisons total192;912 explicit feature-output comparisons target confidence policy while all timing/history/Gaussian helpers remain actual C. The72 calculate caller comparisons use actual model/inference/quality/selection/confidence/output;earlier processing stages remain controlled boundaries. Only45 guarded typed model callback fields are normalized;C execution has no mapped stock code.

Mapped/aligned owners,histories125 and caller125/132,window capacity8 and timing counts0/1/2/125 are tested. Public RAM excludes8192 private stack bytes;void caller scratch/APSR are excluded. Full FPSCR,saved core/FP ABI,SP and masks are checked. Physical hardware,timing,interrupts/concurrency,invalid pointer-owner aliases and allocation failure recovery remain unverified.

All947 normal units compile without failures or duplicate strong symbols;936 prior source/object pairs remain unchanged. Normal provider matches candidate sections and decoded symbols after source-file symbol normalization. The existing r1_goodix_spo2_confidence import closes;application imports drop63 to62,boot imports stay22. This is relocatable composition,not complete bootable firmware. Other health algorithms and hardware/startup dependencies remain open.

[Machine-readable evidence](goodix-spo2-confidence-c-review.json).
