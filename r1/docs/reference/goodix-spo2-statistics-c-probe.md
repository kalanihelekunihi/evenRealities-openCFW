# Native confidence statistics C probe

The ignored candidate at `build/goal-r1-spo2-statistics-c/candidate.c` implements nine native entries:sum61fb4,guarded means61f94/92b68,variance7dcd8,float-count standard deviation61fd4,strided incremental standard deviation61f04,live window deviation66430,last66394 and count66490. It is not a source-manifest unit.

82,688 stock/C comparisons pass:73,728 broad,5,504 conversion/count/alias cases and3,456 independent Fraction-oracle pairs. Broad and targeted conversion/count suites use all32 FP configurations; aliases and oracles use six. All388 instruction bytes/129 starts and24 literal bytes are authenticated through REA. Nine compiled defects are detected.

Preserve sample-first sum NaN priority, guarded zero-count means, separate multiply/add VMLA and VNMLS ordering, unsigned loop/count conversion, signed strided addressing and native sqrtf behavior. Float-count conversion uses the proven C RTZ/FPSCR helper rather than a C cast. Array variance special-cases count1; incremental deviation does not and returns NaN for one finite sample. Empty-window output remains untouched. The live wrapper clears output before rereading count/data, which matters when output aliases record count or samples.

Actual C sqrtf and integer-conversion providers run with no mapped stock executable code. Full public RAM,FPSCR,saved GP/FP registers,SP and masks match. Float results use S0,count uses R0,and the void output wrapper makes no caller-scratch S0 promise. Independent rational mean/variance/sqrt oracles use tolerance2e-5 for rounded statistics and explicitly check empty/one-sample rules.

Before admission:add the shared native header/source unit,verify normal objects and ownership,then wire the confidence dependencies. Confidence's dual-window extractor29144 and its peak/feature/packed helpers remain separate work. Positive oversized float counts,invalid pointer aliases,hardware timing,interrupts/concurrency and physical operation remain unverified.

[Probe evidence](goodix-spo2-statistics-c-probe.json).
