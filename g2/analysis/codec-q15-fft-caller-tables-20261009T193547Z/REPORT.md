# Bounded backup-codec Q15 FFT caller and table binding

**The selected pair is used by a prepared 512-point real-FFT/inverse-FFT call chain in BINH B, with exact stock tables now bound.** This establishes static caller intent and layouts, not live backup selection, CPU alias visibility, physical audio behavior or a source-reproducible build.

## Coordinates and call flow

The locked codec payload SHA is b06dfef7faa2f1e52d2aacd07958d4b96ffc36dca5077ac9149e48f19fc9c4d0. BINH B stage2 equals component bytes[244032,326092). Original loader's normal-copy mapping places these at10003000..1001708C; this remains conditional, with prior sentinel/CPU-alias limits preserved. All CPU addresses below are coordinates under that mapping; bound-ranges.json also retains component coordinates and exact hashes.

The already identified forward530-byte body at package47D3C maps1000F3FC; inverse530-byte body at47F50 maps1000F610. Newly traced complex dispatcher1000F1D4 selects these for fftLen256 and inverse flag0/1, passes table pointer and modifier1, then optionally calls bitreversal1000F824. Real wrapper1000EF64 consumes a20-byte descriptor, uses complex lengthreal_len/2, and chooses forward CFFT→real split or inverse real split→inverse CFFT. Inverse suffix doubles512signed-halfword results with truncating halfword stores. Pseudocode preserves original fixed-point operations rather than asserting float equivalence or C-language behavior for arbitrary signed shifts.

Two coherent caller contexts establish use beyond isolated kernels:1000D3DC is preceded by signed-halfword/window multiplication and arithmetic shift15, then invokes the forward real transform on its scratch/output buffers.1000DC72 invokes the inverse real transform after earlier processing/shift calls, writing state_r17+84's buffer. Descriptors are loaded from literals20017020 and2001700C respectively. Other apparent BSR hits in linear whole-image disassembly are unclassified discovery candidates; no exhaustive caller census or code/data denominator is inferred.

Both descriptor byte sequences are bound in the normal-copy image at IRAM10017020/1001700C; their caller literals refer to DRAM20017020/2001700C. Actual visibility across those aliases remains an existing external/platform boundary. The image statically prepares forward/inverse512, bitreverse1, modifier1, a shared real coefficient pointer100150D8 and complex descriptor100143E4. The latter carries complexlen256, twiddle100145D4, bitrev100143F4, bitrev length240. Original load offsets support both layout contracts; source header agrees. See descriptor-layouts.json.

## Full-table evidence

Fresh comparison against already registered libcsky_dsp.a gives three complete exact matches:

| Table | Conditional IRAM address | Full bytes | SHA-256 |
|---|---|---:|---|
| cskyBitRevIndexTable_fixed_256 |100143F4|480|77f9067a05b953496342be0361b74253f690465994854fd15b78525b72490278|
| twiddleCoef_256_q15 |100145D4|768|9e05c434c0378b8190fb94493619719924accb86c9cd81ffd58f2654f2cc4368|
| realCoefAQ15_512 |100150D8|1024|f02ad5cfc640d3484d44ba4366dd3f20b2883d83600db65dd32bdd8b049434e1|

Total2272bytes. These sizes imply240u16 bit-reversal entries,384Q15 complex-twiddle scalars and512Q15 real-coefficient scalars. The 16-byte archive constant descriptor is **not raw-byte equal** to stock, because pointer fields carry relocations. Its recorded relocation at+4 names twiddleCoef_256_q15 and at+8 names cskyBitRevIndexTable_fixed_256, agreeing with resolved stock pointer destinations. This is relocation/contract agreement, not a silently normalized exact match. No source-byte reproducibility follows from DWARF or these tables.

## Validation and stopping boundary

Static original bytes, target C-SKY disassembly, caller argument flow, descriptor loads and full-table/hash comparisons only. No original-instruction execution, synthetic DSP numerical test, compiler run, hardware action or guest/emulator execution occurred. Compiler/DWARF evidence remains per-object metadata from the preceding scan. Earlier codec symbols have descriptive backup-RFFT/CFFT labels, but their incomplete extents are not reused as a whole-function proof; this packet supplies direct current instruction/table evidence and claims no new admitted corpus coverage.

The finite selected binding is complete. Remaining inputs for stronger claims are CPU alias specification/runtime visibility, proof of BINH B startup selection, upstream invocation roots and initialized state/buffer ownership, and bounded numerical validation for the exact instruction environment. Whole private voice algorithm, microphone routing, frame timing and normal hardware use are outside this batch. Do not reopen unrelated closed audio branches or expand into another shutdown model.
