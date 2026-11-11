# Native packed conversion ABI probe

421,888 exact stock/C comparisons pass for typed5/10 and6/9 pack/unpack wrappers. Six compiled defects are detected,including wrong format and wrong input/output ABI. All282 native instruction bytes/98 starts execute;REA bytes match the locked application.

Probe only; no native provider has yet been admitted to sources.json. The actual portable bit backends are linked through typed wrappers,not renamed or blindly aliased. Generic variable exponent-width kernel entries and array callback28dec remain separate work.

All65536 packed encodings are compared for each format in FP modes0/31. Pack tests use13312 binary32 inputs per format in6 modes. Exact result,FPSCR,saved R4-R11/S16-S31 and SP are checked;public-memory effects,caller scratch/APSR,interrupt masks,timing and physical hardware are outside this scalar probe.

REA returns a width6 thunk for generic kernel requests362f4 and4fdf8. The assembly and disjoint ranges,not specialized pseudocode,establish the hard-float S0/core-register ABI. The stock unpack operation does not map maximum packed exponent to IEEE infinity;the portable bit backend preserves the stock bit construction.

[Machine-readable evidence](goodix-packed-conversion-c-probe.json).
