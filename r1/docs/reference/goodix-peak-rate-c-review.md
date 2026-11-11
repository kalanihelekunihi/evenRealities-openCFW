# Native peak rate in C

`native_peak_rate.c/.h` implements native0x42bd0 without assembly or owned writable state. 30,972 stock/C comparisons pass,including1,452 independent Fraction-oracle pairs. Six compiled defects are detected. All316 instruction bytes/114 starts execute;REA authenticates code and16 literal bytes.

Allocate selected indices before computing the actual C mean;truncate mean to signed integer with native RTZ/FPSCR rules. Select indices using signed raw sample bits >=0x3dcccccd. If at least7 selected,filter against integer-mean converted back to float,using the first selected-count INPUT samples rather than gathering selected amplitudes. Signaling NaN comparisons retain native flags.

Only3..13 retained indices proceed. Allocate actual C gap storage,reject adjacent gap differences above3 and nonpositive span. Compute separately rounded f32(selected-1)*1500/span,then actual C binary32 promotion,software double add-half and signed truncation. Preserve initial output store followed by40..200 clamp stores and exact cleanup order.

Public RAM includes actual C heap allocations and frees. Output/value/index aliases,32 FP configurations,saved core/FP ABI,SP and interrupt masks are checked. The Fraction oracle independently validates equally spaced unit-amplitude rates across6 FP configurations.

Valid mapped/aligned buffers and tested counts0..125 are assumed. Public RAM excludes8192 private stack bytes below SP;void caller scratch/APSR are excluded. Full FPSCR,saved core/FP ABI,SP and masks are checked. Physical hardware,timing,interrupts/concurrency and invalid allocation recovery remain unverified.

All944 normal units compile without new imports or duplicate strong symbols;933 prior source/object pairs remain unchanged. Normal provider matches the candidate sections and decoded symbols after source-file symbol normalization. Normal tests use6 FP modes;the original broad probe uses32. This remains relocatable composition with63 application and22 boot imports,not a complete bootable image. Peak selection,feature extraction,confidence and hardware/startup work remain open.

[Machine-readable evidence](goodix-peak-rate-c-review.json).
