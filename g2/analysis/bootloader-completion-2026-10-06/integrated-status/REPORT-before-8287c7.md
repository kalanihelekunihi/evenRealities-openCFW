# Bootloader source integration status

Current verified immutable image: **44d67f98730a7921f7ef5f1afa22651cdc9e5222753d1f2dcefafad7a89f8fbe**. All seven fresh cases PASS: normal2, malformed3, interruption/reboot2. Stopped/reboot persistence and observables match; both stock/source reach fixture application reset without exception.598 final input hashes and150 linked objects match after validation. One direct runner's descriptive scope was corrected before its93 tests were rerun; executable test logic/image unchanged and prior manifest preserved. [Exact-image validation](same-image-validation-44d67f.json).4cb522,8ec1fa and earlier checkpoints preserved.

Seven-case deduplicated observed original instruction footprint: **36,410/148599 = 24.50218%**, up164 bytes. Bounded modeled execution, not source completeness. Six existing FP64 effects remain modeled; ADC control FP32 executes native original/source instructions. External ROM48 supplies synthetic zero-valued calibration words, not actual factory evidence.

## ADC configuration, control and calibration

[Context/channel configuration](adc-configuration/REPORT.md) is now native:42eb74=54 bytes,42eaf6=126 bytes,93 direct comparisons visit all180 original bytes on this image. Both are reached by stock startup in the seven-case profiles. Channel writes4003800c+4*index before incrementing2002702c; repeated channel configuration increments and wraps. It is not a proven unique-channel count; byte10/11 are not boolean-masked. No child call, allocator or implicit argument null guard.

[Control/getters](adc-control/REPORT.md):279 comparisons/all340 bytes, no FP32 stubs. Request3 copies correction pair ignoring validity; request2 returns a raw marker; warm temperature cache20027028 survives initialization/reset. [Calibration](adc-context/REPORT.md):135 cases/all408 new bytes; static72-byte context is claimed/published before calibration. Failure can return success/defaults/invalid correction with stale pair. Reset clears metadata, not stop/free/drain.

## Preserved regressions and limits

434 GPIO,292 IOM IRQ,505+10 asynchronous event,740 IOM child,12 heap cleanup and2 conditional CQ cases PASS on this image. [GPIO](gpio-descriptors/REPORT.md) stock97 rows request no callbacks; direct descriptor tests model28 original zero-fill bytes due reproduced Unicorn IT/STM issue; higher-bank callback registration outside validated local IRQ table remains unproved. [CMDQ](cmdq-ownership/REPORT.md)40 shared plus13 **separate** termination-module cases PASS; no quiescence/free/drain proof. Synthetic callback reentry is not hardware evidence.

369 alignment mappings PASS; known bad odd31a9b rejected. 60 numeric aliases,39 segments,zero source hash mismatches. [Partial inventory](implementation-inventory-44d67f.json):488 defined function symbols,79770 unique compiled function bytes,56 selected original/source mappings. Counts/sizes do not establish implementation completeness.

## Next actual boundary

[Sample/lifecycle static finding](adc-sample-next.md): numerical correction42ee00 **does** check20027199 before applying the pair, unlike getter request3. The nameadc_normalize42eda0 is misleading: it deactivates/releases clock; actual sample correction is42ee00 and enumeration42ee70. 48 original-only gate/zero-gain-offset fixtures PASS, including the12-bit corrected return mask(bits6..17); no reconstructed-source equivalence claim. Native FP32 nonfusedVMLA/VCVT corners, FIFO/sample layouts and required lifecycle/clock provider remain next work. Profile transfer, apply-profile, activation/enable/disable/command/enumeration, remaining service/RTOS/kernel/startup and complete vectors/assets/data/layout/compiler/byte equality remain open.

The relocated ELF uses prepared objects and external ROM/peripheral/task models. It is not a clean source-complete standalone flashed image or byte-identical firmware. No unrelated app changes, commits, flashing, hardware writes or IAR authentication.
