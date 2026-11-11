# Native confidence statistics in C

`native_spo2_statistics.c/.h` implements nine native entries with no assembly or writable global state.

Nine native entries provide sample-first sum,guarded means,array sample variance,float-count standard deviation,strided incremental deviation,live window deviation,last sample and full16-bit count. Scalar floating results use S0,count uses R0,and the output wrapper is void. These interfaces are distinct from historical portable guessed APIs.

Preserve separately rounded VMLA and VNMLS operation order,including sample-first or accumulator-first NaN priority as appropriate. Signed strides use native modulo32 address arithmetic. Float count converts through the proven C unsigned RTZ/FPSCR helper rather than a C cast. Actual C sqrtf handles the final result and native errno behavior.

Empty means use denominator1. Array variance uses denominator1 for one sample and count-1 otherwise; incremental deviation retains count/(count-1),so a finite one-sample input yields NaN and native FP flags. Empty-window output is untouched. Nonempty window deviation clears output BEFORE rereading count/data; output/count and input aliases preserve those live effects.

Independent Fraction sum/mean/sample-variance and sqrt oracles check finite integer datasets and explicit native empty/one-sample rules with tolerance2e-5 for rounded statistics. Exact stock/C comparisons remain separate evidence. Broad and targeted count-conversion suites use32 FP configurations,with alias/oracle samples using six. Normal broad/conversion samples use six and aliases/oracles two.

REA authenticates388 instruction bytes and24 literal bytes. All388 bytes/129 starts execute. Nine compiled defects detect sum NaN priority,empty mean,one-sample variance,incremental sign/scale,missing conversion status,stale window count,empty last and wrong count-field errors. Source uses no stock executable mapping or algorithm-model fallback.

99,368 exact stock/C comparisons pass,including4,608 independent Fraction-oracle pairs. Nine compiled defects are detected. All940 normal units compile without failures or duplicate strong symbols. All929 prior source/object pairs are unchanged. Normal sections and decoded symbols equal the tested candidate after source-file symbol normalization. Imports remain63 application/22 boot.

Valid mapped samples/records are assumed. Statistical array counts cover0..125 and tested signed strides0/1/2/-1/-2. Count getter covers the full16-bit range. Positive oversized float counts and invalid owner-pointer aliases receive no invented recovery. The void window-output wrapper does not promise caller-scratch S0.

Comparisons check scalar S0/R0 as appropriate,full FPSCR,public RAM excluding8192 private stack bytes below SP,savedR4-R11/S16-S31,SP and interrupt masks. Caller scratch/APSR,traps,timing,interrupts/concurrency and physical hardware remain unverified.

The normal940-unit build remains relocatable composition with63 application and22 boot imports,not a complete bootable firmware. Confidence is not integrated yet; its dual-window feature extractor and peak/packing/correlation dependencies remain open. Other hardware/startup work remains. Source plan and health-cache layout are unchanged.

[Machine-readable evidence](goodix-spo2-statistics-c-review.json).
