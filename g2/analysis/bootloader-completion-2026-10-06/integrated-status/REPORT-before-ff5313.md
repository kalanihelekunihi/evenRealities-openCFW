# Bootloader source integration status

Current verified immutable image: **8287c7b86fea2f84996c517fa1d82b27fd23dd780d923d38db8376bf93e17014**. All seven fresh cases PASS: normal2, malformed3, interruption/reboot2. Stopped/reboot persistence and observables match; both stock/source reach fixture application reset without exception.601 frozen source/runner inputs and151 linked objects match after validation. [Exact-image validation](same-image-validation-8287c7.json).44d67f,4cb522 and earlier checkpoints preserved.

Seven-case deduplicated observed original instruction footprint: **36,804/148599 = 24.76733%**, up394 bytes. Bounded modeled execution, not source completeness. Six existing FP64 effects remain modeled; ADC FP32 native instructions execute without stubs. Resident ROM48 reads are explicit zero-word factory fixtures; ADC readiness/FIFO words are synthetic, not physical conversion evidence.

## ADC sample/lifecycle closure within this model

[Readable behavior, interface, instruction provenance and988 comparisons](adc-samples/REPORT.md). Seven new source-owned bodies total776 original bytes, all visited in direct comparisons. Correction checks validitybyte20027199 and low8 enable; bypass returns unchanged word, enabled path uses original nonfusedVMLA/VCVT semantics and12-bit corrected mask. Temperature input8 bypasses correction. Enumeration returns8-byte sample/slot records; live path can expose20-bit fractional field, supplied-buffer path always shifted14-bit output; requested count0 still processes one record.

Activation sets CFGbit0/contextbit25; trigger enable/disable act on INTTRIGTIMER40038040 bit31, **not IRQ enable**. Software trigger writes37h. Legacyadc_normalize is deactivation: repeat/ADC CFG clearing, clock_release(4,15), metadata flag clearing. Native existing clock dispatcher/provider4/critical/HFADJ code executes in direct absent/last/remaining-user fixtures. No allocator/free, pending-IRQ acknowledgement, scheduler/callback drain or quiescence proof.

[Configuration](adc-configuration/REPORT.md)93 tests/all180 original bytes; [control](adc-control/REPORT.md)279/all340; [calibration](adc-context/REPORT.md)135/all408 new bytes, all PASS on this image. Calibration API0 can leave invalid marker/stale pair; getter3 ignores marker, sample correction respects it. Lazy temperature cache survives init/reset. No actual OTP/calibration/analog accuracy claim.

## Preserved regressions and limits

434 GPIO,292 IOM IRQ,505+10 async,740 IOM child,12 heap and2 conditional CQ comparisons PASS on this image. [GPIO](gpio-descriptors/REPORT.md) stock97 rows request no callbacks; direct descriptor tests model28 original zero-fill bytes due reproduced Unicorn IT/STM issue; higher-bank callback registration unproved. [CMDQ](cmdq-ownership/REPORT.md)40 shared plus13 **separate** termination-module cases PASS, no free/drain/quiescence proof. Synthetic callbacks and FIFO register memory are not hardware observations.

376 alignment mappings PASS; known bad odd31a9b rejected. 54 numeric aliases,39 segments,zero source hash mismatches. [Partial inventory](implementation-inventory-8287c7.json):495 defined function symbols,80560 unique compiled function bytes,63 selected original/source mappings. Counts and sizes are not source completeness.

## Next remaining provider

[ADC profile/apply and required power children](adc-profile-next.md): retained42f020(302B) and42ea68(142B). Transfer calls power-mode enter41bf84/leave41c17a; clock route/class4 already native but required power paths must be traced/reconstructed. Save/restore flag, ordered register image, clock-error early exit and no invented rollback require direct tests. No source completion credited for this static next batch.

Remaining service/post-bringup, RTOS/kernel/ISR/task/startup alternatives and full vectors/assets/data/layout/compiler reproduction remain open. The relocated ELF uses prepared objects and external models; it is not a clean source-complete standalone firmware or byte-identical official payload. No commits, flashing, hardware writes, unrelated applications or IAR authentication.
