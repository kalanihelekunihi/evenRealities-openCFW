# Independent review: bounded radio GPIO consumer

Scope: reconstructed radio GPIO consumer, GPIO117 enable/disable and setup tail, original/source verifier, provenance, tests, and cumulative trace accounting. This review is read-only with respect to implementation and shared evidence.

## Result

No blocking implementation or evidence-integrity defect found in the bounded slice. `comparison-reviewed.json` passes 180 stock/source comparisons and observes 820 unique original instruction bytes for this comparison. Its firmware, ELF and source-manifest hashes match the current locked payload and files. Three focused `test_radio_gpio` methods pass; the aggregate reports 34 modules, 192 tests, 186 passes, no failures/errors and seven skips.

The consumer’s register helper publishes channel 0, pin 117, the reconstructed callback and a null argument. The callback increments the 32-bit counter at `0x20074640`, reads the one-byte handler ID at `0x20074fcb`, then submits event 1 at the proven `WsfSetEvent` entry `0x52b91e`. The verifier intercepts that call on both sides and checks arguments, prior PRIMASK and counter-before-submission; it does not execute the scheduler implementation. The ISR preserves the seven channel-0 status reads in order, restores PRIMASK, reads IRQ59 raw status, clears that mask, then services it. GPIO EN uses a masked read-modify-write under the real PRIMASK provider. Setup reproduces registration, GPIO enable, IRQ59 priority byte `0x40`, then NVIC ISER1 bit 27. The disable wrapper clears GPIO EN bit 21 only.

The stock comparison pins the relevant callback, registration slice, ISR, enable/disable wrappers, boot-tail slice, GPIO-control implementation and NVIC wrappers. The new C is explicitly classified as a reconstruction; only the unchanged GPIO HAL leaves carry the separate Ambiq BSD-3 attribution. The final dependency ranges and source hashes are current. Build provenance and the reconciled inventory bind the reviewed result, ELF, Makefile, and source files.

## Accounting

The 820-byte radio comparison includes shared instructions already traced by earlier batches. Reconciliation by payload identity plus runtime PC contributes 502 new unique bytes, yielding 1,894 cumulative unique trace bytes (234 touch and 1,660 Apollo). The interval intersection records those 502 as unresolved in the initial byte map. The 25-file foundation inventory (10 implementation C, 11 headers, four simulator/seam C files) and all six callable ELF hashes match current files. The profile list is descriptive, not an additive completeness measure.

## Limits and small follow-ups

The scheduler adapter is a fixture boundary. Although the called stock symbol is identified as `WsfSetEvent`, the comparison proves only submitted ID/event values and ordering, not real WSF queue effects, scheduling, initialization, or event delivery. The implementation is a setup tail and pin-specific wrapper, not complete radio boot or teardown. It does not configure physical pads, clear pending GPIO status during disable, unregister the callback, disable NVIC, or wait for an in-flight ISR or queued event. Callback publication writes handler before argument without atomic publication; concurrent replacement, counter races, ISR reentrancy and teardown quiescence remain unproven. W1C and physical interrupt behavior are synthetic/untested.

The verifier uses mixed EN state `0x80400001` for enable, all ones for disable, and zero for setup/ISR; those values cover the relevant unrelated-bit preservation case for enable and disable. The three focused tests check pinned ranges, Make/symbol integration and fail-closed optimized-Python execution. The build integration test does not separately enumerate the new `enable`, `disable`, and `irq_setup` symbols, but the 180-case verifier resolves and executes each symbol in the linked ELF.

No full firmware payload is blob-free, and no source-built byte-identical bundle is demonstrated. Existing binary-backed providers and static/synthetic boundaries remain material.
