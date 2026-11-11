# Native packed conversion in C

`native_packed_conversion.c/.h` implements five native entries without assembly or owned writable global state. 521,664 stock/C comparisons pass;eleven compiled defects are detected. All322 native instruction bytes/113 starts execute.

Typed scalar wrappers preserve native binary32 S0 input/return and packed core-register return. Actual existing C5/10 and6/9 bit backends provide the numerical operation. The maximum packed exponent retains the stock finite binary32 construction rather than an IEEE-half conversion.

Native28dec caches bases,count and callback. Signed nonpositive counts perform no accesses and permit a null callback. Each positive iteration reads a live binary32 input,calls the S0/core callback,and stores only the low halfword before reading the next sample. Overlapping buffers preserve stock mutation order.

REA requests for362f4/4fdf8 resolve to width6 thunks with disjoint generic kernel bodies. Assembly establishes the ABI;specialized pseudocode is not used as width5 proof. The missing width5 pack thunk28dd4 is authenticated directly from six locked bytes. Generic variable-width kernel entry points are not exposed by this unit.

Scalar comparisons verify result,FPSCR,saved core/FP registers and SP. Array comparisons additionally verify public RAM excluding8192 private stack bytes,and interrupt masks. Caller scratch/APSR,timing,physical hardware and interrupt/concurrency behavior remain unverified.

All943 units compile without new imports or duplicate strong symbols;932 previous source/object pairs are unchanged. The normal provider matches tested sections and decoded symbols after source-file symbol normalization. This is relocatable composition,with63 application and22 boot imports,not a complete bootable image. Peak selection,rate extraction,confidence and hardware/startup dependencies remain open.

[Machine-readable evidence](goodix-packed-conversion-c-review.json).
