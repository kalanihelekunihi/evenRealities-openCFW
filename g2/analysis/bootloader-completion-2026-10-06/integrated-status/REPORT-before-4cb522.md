# Bootloader source integration status

Current verified immutable image: **8ec1fa00cae0c882dae79282e43736418537a942645ba185d7a6d6026f5618fb**. All seven fresh cases PASS: normal2, malformed3, interruption/reboot2. Both stopped/reboot persistence and observables match; both stock/source reach the fixture application reset entry without exception.592 frozen source/runner inputs and148 linked objects remain unchanged. [Exact-image validation](same-image-validation-8ec1fa.json).6bef4e and prior checkpoints remain preserved.

Seven-case deduplicated observed original instruction footprint: **36,160/148599 = 24.33395%**, up494 bytes from35666. This is bounded modeled execution, not source completeness. Six FP64 effects and external ROM/peripheral/IRQ/task behavior remain modeled. The new resident ROM48 fixture explicitly supplies zero-valued words for five INFO calibration requests; it is not recovered ROM code or actual factory calibration.

## ADC initialization and calibration

[Readable behavior, layouts, SDK/byte provenance and tests](adc-context/REPORT.md). Initializer42e8d0 and metadata reset42ea32 now have native C with a source-owned static72-byte context at20026df0.135 direct comparisons visit all408 new original body bytes across stated fixtures. [Ownership](adc-source-ownership-8ec1fa.json). INFO selector421548, dispatch4213e6 and thunk41d28a reuse native source; only absent resident ROM48 is controlled.

The context is claimed/published before calibration. INFO or zero-value failure returns init success with temperature defaults/marker0 and invalid correction marker; stale correction pair words can remain. ROM-return errors are discarded by existing dispatch. Raw nonzero bits qualify; finite/ranged float values are not validated here. Reset clears claim/magic metadata, not peripheral state or ownership. No heap allocation/free or IRQ/task/callback quiescence proof.

Downloaded pinned Apollo510 ADC/INFO/register headers corroborate the five calibration fields and word units. [Next static control/getter finding](adc-control-next.md): request3 copies offset/gain without reading correction-valid marker, while request2 publishes raw measured/default0/1. That340-byte family is not source-integrated yet; trace its actual consumer before applying another app-side correction.

## Preserved GPIO/IRQ/queue evidence

434 GPIO,292 IOM IRQ,505+10 asynchronous event,740 IOM child,12 native heap cleanup and2 conditional CQ cases PASS on this image. [GPIO registrar and required children](gpio-descriptors/REPORT.md) remain native; stock97 rows request no callbacks. Direct callback-descriptor tests model original28-byte zero-fill due independently reproduced Unicorn IT/STM failure. Four local IRQ entries56..59 are authenticated; callback-enabled higher-bank descriptors remain outside the partial-image validation domain. Callback/argument publication is borrowed and not protected as an owned lifetime.

[CMDQ lifetime/caller table](cmdq-ownership/REPORT.md):40 shared-image comparisons plus13 termination comparisons PASS with a **separate** retained source module. Term is not linked into this shared image. Cancel rewinds unpublished reservation; forced teardown does not drain, free buffers or notify callbacks. The retained IOM island is fully partitioned, but no absent SDK submit/uninitialize routine is fabricated and global dynamic/inline reachability is not certified.

366 alignment mappings PASS and known odd31a9b image rejected.63 numerical bindings,39 segments,zero source hash mismatches. [Partial linked inventory](implementation-inventory-8ec1fa.json):485 defined function symbols,79244 deduplicated compiled function bytes,53 selected original-to-source mappings. These sizes/counts do not establish a source-complete percentage.

## Remaining bootloader scope

[Completion/provider checklist](remaining-providers-dceae3-worklist.md). ADC control/getters42ec0c, context configuration42eb74, profile/channel/activation/sample APIs and remaining service/post-bringup dependencies remain recoverable next work. Startup alternatives, lower kernel/ISR/task lifetime, logger/fatal, full payload vectors/assets/data/layout, compiler reproduction and byte equality remain unclosed. Real calibration/OTP/analog/IRQ/task quiescence requires evidence outside these synthetic tests.

The relocated ELF uses prepared objects and controlled hardware/ROM fixtures; it is not a clean whole-payload source build, standalone flashed image or byte-identical firmware. No unrelated application changes, commits, flashing, hardware writes or IAR authentication occurred.
