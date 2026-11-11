# Native autocorrelation in C

`native_autocorrelation.c/.h` implements four native entries without assembly or writable global state.

Full correlation92a04 writes into2*max(n,m)-1 words with padding left untouched. Unequal lengths reverse output direction when the second input is longer. Live reads and nonfused sample-first VMLA preserve alias and NaN behavior.

Vector scale928da enters at its compare within body928cc..928df;928ca is a separate veneer. The hard-float ABI supplies factor inS0. Each live sample multiplies sample-first and stores forward; zero count performs no FP operation.

Normalized autocorrelation666a4 allocates count*8-4 bytes using the actual C heap,correlates equal-length inputs,copies the first count words using C memmove,frees the temporary,and calls the actual C maximum-index routine. A signed raw-bit maximum cutoff0x358637bd gates reciprocal scaling. No floating absolute cutoff or invented allocation fallback is substituted.

34,016 stock/C comparisons pass,including360 independent numerical-oracle pairs. Nine compiled defects are detected. All468 instruction bytes/165 starts execute;12 literal bytes are authenticated through REA. All942 normal units compile without failures or duplicate strong symbols;931 prior source/object pairs are unchanged. The normal provider matches the tested candidate sections and decoded symbols after source-file symbol normalization.

Valid mapped/aligned positive lengths for correlation and normalization are assumed;zero-length scaling is covered. No invented input or allocation recovery is added. Public RAM excludes8192 private stack bytes below SP;caller scratch/APSR are outside void contracts. Full FPSCR,saved core/FP registers,SP and interrupt masks are checked. Physical hardware,timing and interrupt/concurrency behavior remain unverified.

Normal build remains relocatable composition with63 application and22 boot imports. Peak selection,packed conversion,rate extraction,confidence parent and other hardware/startup work remain open. Byte identity is waived;source plan and cache layout remain unchanged.

[Machine-readable evidence](goodix-autocorrelation-c-review.json).
