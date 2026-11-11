# Native SpO2 inference parent in C

`native_spo2_infer.c/.h` implements native `0x968c4` and resolves the existing `r1_goodix_spo2_infer` calculate import, with no new assembly or writable global state.

The native five-argument inference entry consumes context/flags pointer references and a generated-model descriptor. Its second argument is unused. Two dimensions are byte products at9*10 and12*13; the first tail is copied as floats and the second is normalized into a2244-byte workspace. The graph receives all seven native arguments, including the exact byte at flags+5. The existing calculate caller now includes the shared typed header; its entire object remains byte-identical.

Both buffers are allocated before history counts are checked. Insufficient history or a nonzero graph status returns5 without freeing, preserving the observed stock leak. Success clamps the predicted value then frees both allocations and returns0. The stock graph currently always returns0; distinct injected-status tests exercise the parent error branch without claiming it naturally occurs in that graph.

Output clamping follows VCMPE carry and signed raw-bit comparison against2.0. Quiet and signaling NaNs raise IOC; FZ affects comparison and IDC without replacing the original stored operand. Positive NaNs clamp to2, while negative NaN payloads can remain. Negative finite values clamp to positive zero; negative zero is retained. A pure C bit/status helper uses compiler FPSCR intrinsics; ordinary C comparisons failed quiet-NaN status before this correction.

Real-graph tests use actual C heap, constructors, model parameters, normalization and all C graph operators. Calculate-caller tests also run the actual quartic and heap, while earlier processing and the four unfinished output stages are explicit controlled boundaries. The source machine has no stock executable mapping. Exactly45 model callback fields are normalized only after verifying their native address/C-symbol identity.

4,444 stock/C comparisons pass:760 real-graph comparisons,3192 explicit graph-status/output-boundary comparisons,456 native calculate-caller comparisons and36 branch-coverage cases. These categories remain distinct. Candidate suites use all32 FP configurations; normal-object samples use six. Nine compiled defects are detected, including dimensions, workspace size, history equality, reset byte, NaN/FZ flags, unsigned clamp and missing success cleanup.

All935 normal units compile without failures or duplicate strong symbols. All923 prior source/object pairs are unchanged; the calculate header-only edit preserves its entire object. Normal parent sections and decoded symbols equal the tested candidate after source-file symbol normalization. Application imports fall67 to66; boot imports remain22.

Valid aligned descriptors and mapped backing storage are assumed; allocation-success paths are tested. No new handling is invented for null allocations, invalid descriptors or undersized caller buffers. Tests cover actual125-sample model geometry and exact/excess/insufficient history, not arbitrary model sizes.

Full public RAM excluding8192 private stack bytes below SP, scalarR0, full FPSCR, savedR4-R11/S16-S31, SP and interrupt masks are compared. Caller scratch/APSR, timing, interrupts/concurrency and physical hardware remain unverified. All290 native instruction bytes/100 starts execute; this is coverage rather than exhaustive input proof.

The normal935-unit build is relocatable composition, with66 application and22 boot imports. It is not a complete bootable firmware image. Output quality, selection, confidence and output packing remain open SpO2 stages, alongside other hardware/startup dependencies. Source-plan qualification and health-cache layout remain unchanged.

[Machine-readable evidence](goodix-spo2-infer-c-review.json).
