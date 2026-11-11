# Native peak-feature metrics in C

`native_spo2_peak_metrics.c/.h` implements native `0x37a84` without assembly or writable global state.

The six-argument native helper appends value1.0 and index length-1 BEFORE iterating through count+1 points. Both arrays require an extra sentinel slot. A signaling positive-value test selects deviations from normalized position(index+1)/full-word length. Sample/index/sentinel aliases retain the exact write/read order,including the zero-used-point branch when an aliased index overwrites the sentinel.

Preserve nonfused squared-error VMLA,signaling reverse absolute difference,sample-first absolute sum and actual C sqrtf RMS. The mean absolute deviation is capped by native SIGNED RAW BITS against half; quality is the native VMLS expression100-(2*mean)*100 with separately rounded operations. This is not a generic RMS replacement.

RMS and quality pointers can overlap each other or values/indices. Outputs store in native order after loop accumulators are cached. Source uses actual reconstructed C sqrtf and maps no stock executable code or algorithm-model fallback. Independent Fraction normalized-position/RMS/quality oracles use tolerances2e-5 RMS and5e-4 score; exact stock/C comparisons remain distinct evidence.

REA authenticates220 instruction bytes and8 literal bytes. All220 bytes/62 starts execute. Ten compiled defects detect missing/reordered sentinels,loop endpoint,positive/unordered gate,absolute direction,cap threshold,quality sign,NaN status and truncated normalization length.

51,200 exact stock/C comparisons pass,including2,048 independent Fraction-oracle pairs. Ten compiled defects are detected. All941 normal units compile without failures or duplicate strong symbols. All930 prior source/object pairs are unchanged. Normal sections and decoded symbols equal the tested candidate after source-file symbol normalization. Imports remain63 application/22 boot.

Valid mapped and aligned extra sentinel capacity is assumed. Tests cover count0..62,full-word normalization length edges and selected data/index/output aliases. Invalid oversized counts or owner-pointer aliases are not assigned recovery.

Comparisons check public RAM excluding8192 private stack bytes below SP,full FPSCR,savedR4-R11/S16-S31,SP and interrupt masks. The void contract excludes caller scratch/APSR. Direct candidate tests use32 FP configurations;aliases/oracles six. Normal direct samples use six,aliases/oracles two. Traps,timing,interrupts/concurrency and physical hardware remain unverified.

The normal941-unit build remains relocatable composition with63 application and22 boot imports,not complete bootable firmware. Confidence/dual-window extraction still need correlation/normalization,peak selection,packed conversion and rate extraction. Other hardware/startup work remains. Source plan and health-cache layout are unchanged.

[Machine-readable evidence](goodix-peak-metrics-c-review.json).
