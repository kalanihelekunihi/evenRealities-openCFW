# Notification-to-PCM foundation

New bounded C source now connects the stock12-byte audio notification, actual ISR queue copy and nonblocking task receive to the age gate and PCM dispatch prefix. Build target: `make -C g2 audio-notification-pcm-simulator`; source: `g2/components/foundation/audio_pcm_consumer/consumer.c` and `consumer.h`. Earlier queue/cache/DMA sources are reused unchanged. No firmware patch, commit, staging, flash or hardware capture occurred.

The latest direct user request was “Let's do a new scan of the same to see what's changed.” That scan was completed first at `g2/analysis/rescan-2026-10-06T011904Z/REPORT.md`; this batch then resumed the parent's authorized notification/PCM foundation request. This report covers actual new implementation and instruction comparisons, not another inventory-only scan.

## New operational knowledge

| Stage | Proven bounded behavior | Ownership consequence |
|---|---|---|
| Notifier53c6b2 | Builds `{type=2,reserved=0,tick}`,12 bytes | No PCM pointer, length or generation token |
| AUD_SendMessage53c638 / ISR put449abe | Copies message into queue; full rejects with resource error; success reaches449238 thread-flags call with400000 | Queue owns copied timestamp metadata; reaching flags provider does not prove task wake |
| Zero-wait task get449b3c /441b0a | FIFO copies12 bytes back, decrements count; empty returns resource error | Message copy is independent of PCM contents |
| Consumer53c6f2 | Unsigned32-bit `now-tick`; accepts0..40 ticks,41+ goes to logging; rollover uses modular subtraction | Fresh timestamp does not select the corresponding DMA period |
| Getter57a7e0 | Queries selected slot, invalidates cache, publishes borrowed pointer +3200; consumer increments20074a9c afterward | No ownership transfer or PCM copy |
| PCM57adf8 prefix | uint8 mode; guards mode≥2/null/zero;12-byte records at20073c20, mode byte+4, callback+8; callback pointer reread beforeBLX | Callback receives borrowed pointer/length; missing mode0 registration goes to DSP fallback, mode1 returns |

`consumer.c` adds real context/tick/scheduler-state wrappers: IPSR/PRIMASK/BASEPRI select task versus ISR context, but both stock tick providers read20074a34. Tick frequency, increment timing and full scheduler behavior are not reconstructed by this read-only counter access. Values are ticks, not milliseconds.

The synthetic sequential scenarios enqueue a timestamp, perform0..3 actual DMA rearm calls before receive, receive the copied message, then invoke the actual consumer prefix. Explicit fixture writes clear NEXTCTRL bits to model peripheral progress. Partial TX-busy returns9 after RX selection advances; the later consumer queries that current selection. Buffer-content mutation after cache handoff reaches the callback boundary unchanged because neither queue nor prefix owns a PCM copy. These results demonstrate stock read/use order and feasible schedules in a model, not a field race or a lifetime-safe design.

## Validation

Final saved original/source comparison: **PASS328 calls**, **1,312 distinct traced original instruction bytes**, authenticated against Apollo SHA-256 `36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863`, header32, load438000, little-endian Thumb/M-class. SourceO2 uses a Cortex-M4 compatible instruction profile; Apollo510 hardware is Cortex-M55.

Cases cover scheduler/context combinations, ages0/1/40/41/42/high-bit/max across tick rollover; low-byte modes and invalid pointer/length; callback presence/mode mismatch and reread; queue fill/full/empty/FIFO wrapping with timestamps0/max/high-bit; repeated rearms, partial TX failure and borrowed-content changes. Registered callbacks, DSP, logger and task wake providers are never replaced with executable fake returns. Those runs stop before their original entries while the stock frame remains live; the C prefix returns a NEW observation descriptor, not a claimed stock ABI result.

The final observer hooks only the fields it measures. An earlier broad memory hook changed original instruction execution: after stock memcpy439be4, it skipped unconditional LDR441f0c, advancing a12-byte queue pointer by24 instead of12. `hook_profile_diagnostic.py` freshly reproduces both profiles with unchanged bytes: scoped advances12 and includes the load; broad advances24 and skips it. `hook-profile-results.json` and `first-verifier.py` preserve the rejected profile. No source or original instruction was changed to compensate; diagnostic traces receive no coverage credit. This identifies an instrumentation-dependent native engine limitation, not its internal cause. Existing optimized tick failure remains separately blocked.

Deduplicated instruction evidence adds **486 new bytes**, overlapping826 earlier bytes; cumulative **7,912** =touch234 +Apollo7,678, from25 saved evidence inputs. Foundation now contains87 C/header files. Counts are bounded original instruction evidence, not complete source coverage or compiled byte equality. Newly integrated ELF leaves older ELF/results untouched. Fresh aggregate:44 modules,228 method tests,222 passes,6 method skips plus1 setup skip, zero failures/errors. Affected checks:8 passes. Independent reviewer reran13 native representative stock/source comparisons. Exact bindings are in `validation-summary.json` and `review/`. The aggregate used repository PYTHONPATH and bounded npm dependency retries; the initial npm-retry interruption and import-path failure remain retained as diagnostics, with no product-source change.

## Remaining boundaries and practical implications

The actual449238 flags-set provider, audio thread wait/context switch and initialized dispatcher RAM table20073fbc are outside runtime validation. Static drain53cd62 uses zero-timeout get and aud_dispatch53c5ac; flags53cdac test bits22/23 (400000/800000). The sequential tests explicitly invoke the consumer after get. They do not execute the full audio task's routing or establish that table type2 was initialized to this handler in a booted system.

Fixtures use coherent12-byte data queues with unlocked TX and empty send/receive waitlists. Scheduler unblock455370, mutex disinherit45596e and assertion paths are declared unexecuted source boundaries, not implemented providers. Blocking/task-submit/ISR-receive paths, real initialized TCB/waitlist transitions, tick progression and startup ownership remain unverified.

A ring/app/CFW client must not interpret “fresh” as an immutable audio sample. An owned-buffer design needs a period identity or snapshot tied to the producer and a proven no-reuse/copy interval; cache invalidation alone supplies neither. The next foundation batch should execute the real task-flags set/wait and initialized audio dispatch table, or reconstruct a registered callback/DSP consumer's first actual PCM reads. Deciding hardware lifetime requires producer/interrupt/consumer scheduling or hardware evidence not present here. No whole-image source-complete or byte-identical bundle claim is made.

## Navigation

- `audio-stream-2026-10-01/`: stock PCM registration,205-byte body and LC3/DSP call boundaries;26 original scenarios with explicitly stubbed algorithm/codec/transport providers.
- `audio-ble-metadata-2026-10-01/` and `ess-gatt-2026-10-01/`: prior outer transport/GATT knowledge; consult their own provider/MTU limits.
- `audio-cache-handoff-2026-10-06/`: query/getter/cache source and separate new bounds policy;282 stock/source +1,157 policy cases.
- `audio-dma-rearm-2026-10-06/`: next-buffer programming and IRQ prefix;899 scenarios/1,019 calls, notifier previously unexecuted.
- This directory: actual12-byte queue copy/receive, age gate and PCM dispatch prefix; wake/consumer routing/callback execution remain bounded.
