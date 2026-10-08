# Bootloader source integration status

Current verified immutable image: **6bef4edbcece2022ee41b9670cd4eff295fc62bb697e00e180c4efce8812c259**. Seven fresh cases PASS: normal2, malformed3, interruption/reboot2. Both stop/reboot persistence and observables match; both sides reach the fixture application reset entry without exception.589 frozen inputs and147 linked objects remain unchanged. [Exact-image validation](same-image-validation-6bef4e.json). Prior4f111c and earlier checkpoints remain preserved.

Seven-case deduplicated observed original instruction footprint: **35,666/148599 = 24.00151%**, up198 bytes from35468. This is bounded modeled execution, not source-complete percentage. Six original FP64 effects remain modeled; physical MMIO/ROM/cache/task/IRQ behavior is outside the offline model. Source completeness, whole-payload build and byte equality remain separately unproved.

## Native GPIO initializer

[Registrar behavior, source interfaces, original instruction evidence and table](gpio-descriptors/REPORT.md). Native registrar430280 processes the source-defined97-row/1164-byte descriptor table at42f674. Five required child bodies—status41dcca, clear41de3c, callback-register41e000, control41da84 and priority43025c—are native; pin configuration/state and NVIC reuse existing source.434 direct comparisons PASS, visiting1720 of1726 new mapped body bytes. Six guarded/impossible instruction bytes are separately identified, not counted as visited. [Partial ownership](gpio-source-ownership-6bef4e.json).

Stock descriptor types1/2/4 configure/output pins; type3 is ignored by this registrar. All six stock type2 rows have mode0/callback0, so shared startup does not take IRQ registration. Direct fixtures cover that branch, including the channel-wide pending-status clear, callback-before-argument stores, pin enable, priority4 and NVIC enable. Original28-byte local zero-fill is explicitly modeled in those fixtures because installed Unicorn misexecutes its IT/STM carry loop; an isolated reproducer is preserved. No such model is required by the stock97-row startup.

Local IRQ map has only four entries56..59, followed by text. The partial source image emits only those entries, and callback-enabled higher-bank descriptors remain outside the validated domain. No fabricated mappings, safe ownership, allocator/free, IRQ quiescence or hardware delivery claims are made.

## Affected regressions and retained ownership boundaries

292 IOM IRQ,505+10 asynchronous event,740 IOM child,12 native heap cleanup and2 conditional CQ cases PASS on this exact image.364 alignment mappings PASS; known bad odd31a9b placement remains rejected.65 numerical bindings,38 segments,zero source hash mismatches. [Linked inventory](implementation-inventory-6bef4e.json):483 defined function symbols,78802 deduplicated compiled function bytes and48 selected original-to-source mappings; compiled sizes are not original implementation coverage.

[CMDQ lifetime table and callers](cmdq-ownership/REPORT.md):40 reservation/post/cancel comparisons PASS on this image plus13 termination comparisons in an explicitly **separate retained module** from the frozen object. Termination is not linked into the shared image. Cancel rewinds an unpublished reservation; forced term clears issued register bits/claim without draining, notifying callbacks or freeing supplied buffers. No physical ownership reclamation is inferred.

The IOM island42c034..42cdb0 is partitioned into18 accounted bodies/3424 instruction bytes and28 literal bytes. Standalone SDK IOM submit/full/uninitialize APIs are not retained there; global inline/dynamic reachability is not certified and vendor SDK replacements are not invented. Native IOM IRQ/status/clear, async publication/service and prior allocator/CQ/clock/claim/semaphore bodies remain validated with their original limits.

## Still open

[Current provider checklist](remaining-providers-dceae3-worklist.md). Next actual initializer dependency is ADC context42e8d0..42ea32: [instruction-derived next finding](adc-next.md). It claims/publishes a static72-byte context before calibration reads; failure uses defaults/validity markers instead of rolling back the claim. No ADC source integration is claimed at this checkpoint. Remaining ADC, service/post-bringup, kernel/ISR/task lifecycle, logger/fatal, full vectors/assets/data/compiler reproduction and physical behavior remain unclosed.

Relocated test ELF uses prepared objects and bounded synthetic fixtures. It is not a clean whole-firmware source build, standalone hardware image or byte-identical artifact. No broader GPIO component changes, commits, flashes, device writes or IAR authentication occurred.
