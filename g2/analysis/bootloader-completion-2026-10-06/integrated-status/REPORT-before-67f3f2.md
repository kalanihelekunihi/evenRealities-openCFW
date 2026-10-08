# Bootloader source integration status

Current verified immutable image: **ff53136b29001e2a88deeb93b968bb69fcfe56bcaea576cdf57bc201fbed7911**. All seven fresh cases PASS: normal2, malformed3, interruption/reboot2. Stopped/reboot persistence and observables match; both stock/source reach fixture application reset without exception.604 frozen source/runner inputs and152 linked objects match after validation. [Exact-image validation](same-image-validation-ff5313.json).8287c7 and earlier checkpoints preserved.

Seven-case deduplicated observed original instruction footprint: **37,018/148599 = 24.91134%**, up214 bytes. Bounded modeled execution, not source completeness. Six existing FP64 effects remain modeled. ROM40/48, factory values, FIFO/ready, power acknowledgement, hardware timing and task/IRQ scheduling are explicit models or outside demonstrated scope.

## Native ADC profile/apply and power dependencies

[Profile save/restore, ordered register writes, tests and native child limits](adc-profile/REPORT.md):42f020(302B),42ea68(142B) new source;650 direct PASS/all444 body bytes visited. Existing native power enter41bf84/leave41c17a, descriptor/release-needed/callback/hooks, critical save, status poll/delay and clock/class4 execute for user15. Direct external ROM40 cyclewait and optional callback bodies are controlled; power acknowledgement fixed for success/timeout. Stack-local clock callback pointer addresses normalized after mapped-stack check; lifetime not certified.

Power enter/leave errors are ignored by transfer; restore clock error returns without rollback and leaves saved-validflag set. Snapshot operations1/2 share behavior and do not inherently drain/stop. Restore programs CFGenable last before interrupt enable. Apply requires first clock byte2 and propagates clock failure before CFG write. API0 is not a physical power/calibration/shutdown guarantee.

[ADC region map](adc-region-map-ff5313.json) accounts14 contiguous source-mapped functions/2148 instruction-body bytes+24 float literal bytes+2 alignment bytes in42e8d0..42f14e. This is component accounting, not whole bootloader completeness or code elsewhere/physical behavior certification.

## Preserved tests and interfaces

[Samples/lifecycle](adc-samples/REPORT.md)988 tests/all776 bytes; [configuration](adc-configuration/REPORT.md)93/all180; [control](adc-control/REPORT.md)279/all340; [init/calibration](adc-context/REPORT.md)135/all408 new bytes, all PASS on this image. Count0 processesone record; TEMPchannel8 bypasses correction; validity0 returns sample unchanged; correction mask retains12 bits. Timer enable/disable40038040 is distinct from IRQ enable; deactivation is no proven task/IRQ/callback drain. Getter ignores correction marker while sample helper checks it; temperature cache survives init/reset.

434 GPIO,292 IOM IRQ,505+10 async,740 IOM child,12 heap and2 conditional CQ comparisons PASS on this image. Direct GPIO original28-byte zero-fill is modeled due reproduced Unicorn IT/STM issue, higher-bank callbacks unproved. CMDQ40 shared+13 separate termination-module cases PASS; separate module not shared ELF, no quiescence/free proof.

378 alignment mappings PASS; known bad odd31a9b rejected. 52 numeric aliases,39 segments,zero source hash mismatches. [Partial inventory](implementation-inventory-ff5313.json):497 defined function symbols,80962 unique compiled function bytes,65 selected original/source maps. Counts/segment sizes are not implementation completeness.

## Next remaining bootloader provider

[Post-context constructor422ad4](post-context-next.md):212B no child calls, static4×0x11c pool20024400, publishes real handles into post rows currently left0 by return stub. Native configure422ba8 may be reused; downstream validate42308e/activate422dc6/finish4236ce must be traced under real handles. This next note is static only, no closure credited. Service/RTOS/kernel/startup alternatives/logger/fatal/full vectors/assets/data/layout/compiler reproduction and byte equality remain open.

The relocated ELF uses prepared objects and external models; not a clean source-complete standalone firmware or byte-identical official payload. No commits, flashing, hardware writes, unrelated apps or IAR authentication.
