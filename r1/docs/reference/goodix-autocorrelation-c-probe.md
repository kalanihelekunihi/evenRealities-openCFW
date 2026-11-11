# Native autocorrelation C candidate

31,790 stock/C comparisons pass,including270 independent numerical-oracle comparisons. Nine compiled defects are detected. REA bytes match the locked application for468 instruction bytes and12 literal bytes. All468 code bytes/165 instruction starts execute.

Full correlation92a04 writes into2*max(n,m)-1 words with padding left untouched. Unequal lengths reverse output direction when the second input is longer. Live reads and nonfused sample-first VMLA preserve alias and NaN behavior.

Vector scale928da enters at its compare within body928cc..928df;928ca is a separate veneer. The hard-float ABI supplies factor inS0. Each live sample multiplies sample-first and stores forward; zero count performs no FP operation.

Normalized autocorrelation666a4 allocates count*8-4 bytes using the actual C heap,correlates equal-length inputs,copies the first count words using C memmove,frees the temporary,and calls the actual C maximum-index routine. A signed raw-bit maximum cutoff0x358637bd gates reciprocal scaling. No floating absolute cutoff or invented allocation fallback is substituted.

Probe only: candidate remains under ignored build and is not yet admitted to the source manifest. Positive lengths are required for correlation and normalization; vector scale supports zero count.

Public RAM,full FPSCR,saved core/FP registers,SP and masks are compared. Private8192-byte stack region,caller scratch registers and APSR are excluded. The independent numerical oracle checks mathematical lag indexing and normalized energy. Physical hardware,timing,interrupts and invalid input recovery remain unverified.

Confidence,peak selection,packed conversion,rate extraction and overall firmware boot integration remain open.

[Machine-readable evidence](goodix-autocorrelation-c-probe.json).
