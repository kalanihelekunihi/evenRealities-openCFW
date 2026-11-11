# Native SpO2 output quality in C

`native_spo2_output_quality.c/.h` implements native `0x44a78` and resolves its existing calculate import. No assembly or writable global state is added.

The native four-argument output-quality stage updates its channel record after inference. A nonzero whole summary flag byte resets counter0; otherwise it saturates at255. The actual C rolling-window helper pushes the adjusted prediction. The latest value is promoted to software binary64, rounded by adding0.5 and converted through the native software signed conversion. Configuration chooses the positive signed-byte window length and unsigned-byte spread threshold.

The stage uses actual C max/min helpers on the recent window, or threshold+1 and zero when history is short. Preserve the signaling comparison, reverse subtraction path, final spread comparison and insufficient-history bit2/range bit7. Counter21 uses the LOW THREE summary bits rather than the whole flag byte, with independent saturation at255. These policies are deliberately separate.

The existing calculate caller includes the shared native header and calls this C provider directly. Caller tests run the actual C calculate/quartic, heap, inference parent, model constructors, graph and output-quality stage. Earlier processing and the three unfinished selection/confidence/output stages are explicit test boundaries. Only45 enumerated model callback fields are normalized after exact symbol/address checks; no arbitrary data differences are normalized.

Actual-helper direct tests cover344 of348 native instruction bytes. The retained4-byte reverse subtraction at0x44b92 cannot arise from ordinary same-span extrema over the tested mapped public-buffer contract. Separate injected max/min boundary comparisons exercise that instruction, preserving NaN/FZ/IOC behavior. They are not counted as actual extrema-helper algorithm evidence. REA authenticates348 instruction bytes and12 bytes of literals, including binary64 half and binary32 zero.

40,584 stock/C comparisons pass:38,912 actual-helper comparisons,456 actual calculate/model/inference/quality caller comparisons and1,216 explicit extrema-boundary comparisons. Separately,4,864 independent integer oracles check history, policy, counters, spread/status and FPSCR. Nine compiled defects are detected. The348 instruction bytes/115 starts are covered with the real-helper versus boundary distinction above.

All936 normal units compile without failures or duplicate strong symbols. All924 prior source/object pairs are unchanged; the calculate header edit preserves its entire object. Normal sections and decoded symbols equal the tested candidate after source-file symbol normalization. Application imports fall66 to65; boot imports remain22.

Valid aligned descriptors/backing spans, positive signed window lengths and the single-channel native contract are assumed. Source retains native unchecked behavior for invalid zero/negative lengths and undersized storage rather than inventing a fallback. Arbitrary public aliases, interrupts and concurrent mutation are not established for this stage.

Comparisons check public RAM excluding8192 private stack bytes below incoming SP, full FPSCR, savedR4-R11/S16-S31, SP and interrupt masks. Caller scratch/APSR and native incidental restored argument registers are outside the void C contract. Candidate suites use all32 FP settings; normal-object samples use six. Timing and physical hardware are unverified.

The normal936-unit build remains relocatable composition, with65 application and22 boot imports. It is not a complete bootable firmware image. Three later SpO2 stages, other hardware dependencies and startup remain open. Source-plan qualification and health-cache layout are unchanged.

[Machine-readable evidence](goodix-spo2-output-quality-c-review.json).
