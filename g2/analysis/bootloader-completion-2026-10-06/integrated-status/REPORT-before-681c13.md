# Bootloader source integration status

Current verified immutable image: **3fcec29fcb46ed94547539c5d04c9258fb01070c3f19ad4bf1a7a91efef795ec**. All seven fresh cases PASS: normal2, malformed3, interruption/reboot2. Stopped/reboot persistence and observables match; both stock/source reach fixture application reset without exception. 614 recorded source/runner inputs and 154 linked objects match after validation. [Exact-image receipt](same-image-validation-3fcec2.json). Previous67f3f209, ff53136b and earlier snapshots preserved.

Seven-case deduplicated observed original instruction footprint: **38534/148599 = 25.93153%**, up166 bytes from67f3f2. This is bounded modeled execution, not implementation completeness. Six existing FP64 effects remain modeled; ROM40/48, factory values, FIFO/ready, power acknowledgement, hardware timing, IRQ/task scheduling and drain are explicit models or outside demonstrated scope.

## EasyLogger records and native constructor

[Source, address/hash provenance, ownership and limits](service-records/REPORT.md): seven new bodies176 original instruction bytes,112 direct comparisons PASS/all bytes visited. Guard returns0 even on allocation failure; failure retries later, existing handle is retained. Five33-byte logger records clear without clearing the preceding header. Timeout1000 has no proven time units. Native constructor416610 uses source-owned `elogMutex` attributes and static80-byte storage20026cb0; [focused reset comparison](service-startup-state-3fcec2.json) PASS. Lower acquire/release kernel ownership remains open.

[129 enabled-clock comparisons](clock-shared-3fcec2.json) PASS on this ELF without stock executable bytes in the source machine. PLL timeout→duplicate request→release→request returns4,0,0,4 in controlled fixtures; duplicate request skips lock retry. Physical PLL lock/timing and actual scheduling remain unproved.

Current395 alignment mappings PASS,37 numeric aliases at29 addresses,42 segments,zero receipt source hash mismatches. [Partial inventory](implementation-inventory-3fcec2.json):517 defined function symbols,83,250 unique compiled function bytes,85 selected maps; these are not whole-payload completion metrics. All listed peripheral regressions rerun PASS on3fcec2; CMDQ13 termination cases still use a separate module. Earlier checkpoint-specific reports below remain historical evidence.

## UART constructor and real-handle startup

[Readable source, layouts, lifecycle and limits](uart-context/REPORT.md): constructor 422ad4, accepted power 422ba8, activation 422dc6, baud 422e28, configuration 42308e, status/mask4236ce/423700, ring 4275ea and three NVIC leaves. 1,040 direct comparisons PASS; all 1,652 instruction bytes visited. Existing mode-one callback 41f8ba reused. Static four-context pool 20024400..20024870 is source-owned. Constructor error precedence and selective retained-byte initialization match; no independent selected-pool occupancy check. Activation borrows buffers without allocation/copy/free.

[Focused exact-image reset-state comparison](uart-startup-state-67f3f2.json) PASS: rows 1/2/3 publish 2002451c/20024638/20024754; all 1,136 pool bytes, row values, registers, ordered writes and clock ownership match at actual row-loop return. Final initialized=0 / saved-valid=1 / CFG=0, not active UART service. Row 3 retains borrowed TX buffer 20080800, capacity 1,024. Clock/power errors can be ignored, configuration failures retain partial writes, save/down clears status without proving IRQ/DMA/task drain. Class 6 feature-disabled path tested; enabled PLL success outside this fixture.

Newly recorded NVIC priority bytes exposed an old full-register-versus-byte-store comparison error. Recorder now compares actual store widths; failed-run and intermediate recorder edit-error logs retained. [Memory evidence](uart-context/store-width-evidence.json). All final cases use corrected recorder.

At prior67f3f2:388 alignment mappings PASS; known bad odd31a9b rejected;42 numeric aliases,40 segments, zero source hash mismatches. [Partial inventory](implementation-inventory-67f3f2.json):509 defined function symbols, 83,040 unique compiled function bytes, 77 selected original/source maps. Counts and segment bytes are not an implemented percentage; general 64-bit division is not mapped as complete.

## Native ADC profile/apply and power dependencies

[Profile save/restore, ordered register writes, tests and native child limits](adc-profile/REPORT.md):42f020(302B),42ea68(142B) new source;650 direct PASS/all444 body bytes visited. Existing native power enter41bf84/leave41c17a, descriptor/release-needed/callback/hooks, critical save, status poll/delay and clock/class4 execute for user15. Direct external ROM40 cyclewait and optional callback bodies are controlled; power acknowledgement fixed for success/timeout. Stack-local clock callback pointer addresses normalized after mapped-stack check; lifetime not certified.

Power enter/leave errors are ignored by transfer; restore clock error returns without rollback and leaves saved-validflag set. Snapshot operations1/2 share behavior and do not inherently drain/stop. Restore programs CFGenable last before interrupt enable. Apply requires first clock byte2 and propagates clock failure before CFG write. API0 is not a physical power/calibration/shutdown guarantee.

[ADC region map](adc-region-map-ff5313.json) accounts14 contiguous source-mapped functions/2148 instruction-body bytes+24 float literal bytes+2 alignment bytes in42e8d0..42f14e. This is component accounting, not whole bootloader completeness or code elsewhere/physical behavior certification.

## Preserved tests and interfaces

[Samples/lifecycle](adc-samples/REPORT.md)988 tests/all776 bytes; [configuration](adc-configuration/REPORT.md)93/all180; [control](adc-control/REPORT.md)279/all340; [init/calibration](adc-context/REPORT.md)135/all408 new bytes, all PASS on this image (regressions rerun for 67f3f2). Count0 processesone record; TEMPchannel8 bypasses correction; validity0 returns sample unchanged; correction mask retains12 bits. Timer enable/disable40038040 is distinct from IRQ enable; deactivation is no proven task/IRQ/callback drain. Getter ignores correction marker while sample helper checks it; temperature cache survives init/reset.

434 GPIO,292 IOM IRQ,505+10 async,740 IOM child,12 heap and2 conditional CQ comparisons PASS on this image (regressions rerun for 67f3f2). Direct GPIO original28-byte zero-fill is modeled due reproduced Unicorn IT/STM issue, higher-bank callbacks unproved. CMDQ40 shared+13 separate termination-module cases PASS; separate module not shared ELF, no quiescence/free proof.

Previousff5313 inventory/alignment retained as historical evidence; current metrics are above.


## Remaining providers

[Exhaustive current linker-provider ledger and additional source gaps](remaining-providers-current.md):37 aliases at29 addresses comprise30 aliases at22 OTA addresses,4 synthetic test addresses and3 external resident-ROM addresses. Duplicate aliases are not distinct missing functions. Additional kernel/scheduler/lifecycle, dynamic handlers, full vectors/assets/data/layout/compiler and byte equality gaps remain.

Next milestone: integrate existing acquire4166aa/release416710 wrappers, then recover plain take41a24e/tagged take419e22/tagged give419de2 before claiming mutex ownership or blocking closure. EasyLogger static handle selects plain take; plain release can reuse native queue put. No drain or owned-buffer patch is certified.

The relocated ELF uses prepared objects and explicit models. It is not a clean source-complete standalone firmware or byte-identical official payload. No commits, flashing, hardware writes, unrelated app changes or IAR authentication.
