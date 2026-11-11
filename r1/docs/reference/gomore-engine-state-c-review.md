# Native GoMore engine-state initialization in C

`native_gomore_engine_state.c/.h` implements two native entries without assembly or owned writable global state. 8,704 exact stock/C comparisons pass. Seven compiled defects are detected. All174 instruction bytes/50 starts execute;REA authenticates code and8 literal bytes.

Header71714 clears exactly0x1f8 bytes,then writes native raw -1.0 sentinels,the eight-word140..15c history,ffffffff sentinels164/168,halfword180,mode bytes0c/34/94/1c0,and the exact initial bounds54/58/5c. Logical store order and untouched neighboring RAM are preserved. No FP arithmetic or writable global state is introduced.

State71db6 clears exactly0x3894 bytes,caches and stores the previous-state pointer word at3890,then calls the actual C header initializer. Pointer arguments may refer inside the cleared record because the pointer value is saved rather than dereferenced. Actual C memset executes;no opaque memory-provider fallback is used.

Mapped,word-aligned ordinary RAM records are assumed. Four buffer positions,eight prior-pointer values andfour poison bytes are covered across all32 FP configurations;the normal object repeats two modes. Public RAM excludes8192 private stack bytes below SP;void caller scratch/APSR are excluded. Full FPSCR,saved core/FP ABI,SP and masks are checked. Physical hardware,timing,interrupt/concurrency and MMIO write transaction semantics remain unverified.

All948 normal units compile without new imports or duplicate strong symbols;937 previous source/object pairs are unchanged. Normal provider matches candidate sections and decoded symbols after source-file symbol normalization. Imports remain62 application/22 boot. The native lifecycle initializer6fea0 remains unresolved:filter coefficient construction,profile conversion,composite reset and authorization/runtime checks still need native integration. Portable scratch/bool APIs remain separate contracts.

This remains relocatable source composition,not complete bootable firmware. Source-plan selection and native health-cache layout are unchanged.

[Machine-readable evidence](gomore-engine-state-c-review.json).
