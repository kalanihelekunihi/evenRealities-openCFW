# Native peak selection in C

`native_peak_selection.c/.h` implements three entries without assembly or owned writable state. 5,508 stock/C comparisons pass,including612 independent oracle pairs. Seven compiled defects are detected. All610 instruction bytes/214 starts execute;REA authenticates code and8 descriptor/table-pointer bytes.

Minimum-row668dc loads signed16 input0 before zeroing the output index,then keeps the earliest strict minimum with a16-bit wrapped loop index. Count0 still reads input0 and writes output0.

Mask66900 caches u16 length/row count,allocates and zeros a packed bit matrix,marks triangular boundaries,and checks left then right neighbors using signaling comparisons. Native unsigned BHI conditions accept unordered NaNs;the C comparison flags preserve this behavior and short-circuit order. Actual zero-filling C heap row sums feed signed16 earliest-row selection. Output u16 counts accumulate existing values through the selected row inclusively.

Indices36734 allocates its zeroed mask,uses the locked descriptor row count37,and scans from index1. Zero-mask candidates and equal adjacent plateau samples with neighboring mask counts1 can qualify. Preserve signed begin+1/capacity comparisons,signed16 selected-counter increments,live aliases,halfword index stores,and final count store before freeing the mask.

Public RAM excludes8192 private stack bytes below SP;void caller scratch/APSR are excluded. FPSCR,saved core/FP registers,SP and interrupt masks are checked. Helpers use32 FP configurations;parent uses4 and aliases6. Timing,physical hardware and interrupts/concurrency remain unverified.

Valid aligned/mapped buffers are assumed. Direct mask probes use1<=rows<=length<=125;parent lengths37/75/125 use37 rows. Minimum helper counts0..125 are tested;counts above65535 wrap indefinitely in stock and no recovery is invented. Invalid descriptors,large counts and allocation recovery remain outside the tested domain.

All945 normal units compile without new imports or duplicate strong symbols;934 prior source/object pairs remain unchanged. Normal provider matches candidate sections and decoded symbols after source-file symbol normalization. The original helper probe uses32 FP modes;normal helpers2,parent4,aliases6. This remains relocatable composition with63 application and22 boot imports,not complete bootable firmware. Feature extraction,confidence and hardware/startup dependencies remain open.

[Machine-readable evidence](goodix-peak-selection-c-review.json).
