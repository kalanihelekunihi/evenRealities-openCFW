# Bootloader source integration status

Current verified immutable image: **4cb522cf7cbeffc853a2b2f5428abbd8b9ec8584071c59eb34d30b609a478b8a**. All seven fresh cases PASS: normal2, malformed3, interruption/reboot2. Both stopped/reboot persistence and observables match; both stock/source reach fixture application reset entry without exception.595 frozen source/runner inputs and149 linked objects remain unchanged after validation. [Exact-image validation](same-image-validation-4cb522.json).8ec1fa and earlier checkpoints preserved.

Seven-case deduplicated observed original instruction footprint: **36,246/148599 = 24.39182%**, up86 bytes. Bounded modeled execution, not source completeness. Six existing FP64 effects remain modeled; new ADC control FP32 executes original/source instructions without stubs. Explicit zero-valued resident ROM48 reads for five INFO fields are synthetic factory fixtures.

## ADC control and calibration

[Control/getter behavior, layouts, pseudocode and provenance](adc-control/REPORT.md): native42ec0c..42ed60,279 direct PASS covering340 original body bytes. Requests truncate to8 bits; window bounds20 bits; getter sentinelc2f6e979; raw temperature marker0/1; correction getter ignores validity marker. Cold temperature cache executes individually rounded FP32 operations; warm cache20027028 survives init/reset. API success does not imply valid calibration, fresh correction values or a refreshed temperature intercept. Stock startup invokes request3 for logging; sample normalization remains to trace.

[Initialization/calibration](adc-context/REPORT.md):135 cases,408 new body bytes. Static72-byte claimed context and native INFO chain retained; missing ROM48 only controlled. Claim/output precedes calibration; failure can return success/defaults/invalid marker with stale correction pair. Reset clears claim metadata, not peripheral stop/free/quiescence.

## Preserved regression evidence and limits

434 GPIO,292 IOM IRQ,505+10 asynchronous event,740 IOM child,12 native heap and2 conditional CQ cases PASS on this exact image. [GPIO](gpio-descriptors/REPORT.md) stock97 rows request no callbacks; direct descriptors model28 original zero-fill bytes due independently reproduced Unicorn IT/STM issue. Four local IRQ entries56..59 authenticated; callback-enabled higher-bank behavior outside validated domain. [CMDQ](cmdq-ownership/REPORT.md)40 shared plus13 **separate** termination-module cases PASS, with no free/drain/quiescence proof. Synthetic callback reentry is not hardware behavior.

367 alignment mappings PASS; known bad odd31a9b rejected. 62 numeric aliases,39 segments,zero source hash mismatches. [Partial inventory](implementation-inventory-4cb522.json):486 defined function symbols,79592 unique compiled function bytes,54 selected original/source mappings. Counts and sizes are not implementation completeness.

## Next bounded gap

[ADC context/channel configuration](adc-configuration/REPORT.md): next54+126 original bytes reconstructed,93 direct comparisons PASS in a separately retained leaf ELF. No child calls; context encodes40038040; channel writes4003800c+4*index then increments2002702c including repeats/wrap. This leaf is **not shared-image integrated**, not counted in the seven-case numerator. Remaining profile/activation/enable/command/sample/normalization paths and service/RTOS/kernel/startup alternatives remain open.

The relocated ELF uses prepared objects and external peripheral/ROM/task models. Full vectors/assets/data/layout, compiler reproduction, source-complete standalone operation and byte equality remain unproved. No commits, flashing, hardware writes, unrelated application changes or IAR authentication.
