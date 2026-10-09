# Current bounded dependency-source results

| Batch | Newly recovered bodies | Validation / limit |
|---|---|---|
| [Queue/CMSIS](../audio-queue-cmsis-source-closure-2026-10-09/REPORT.md) | Generic send/receive +2 private copies,3 context/wrapper,5 block/timeout helpers |1345 mixed comparisons +504 timeout; source-only exercised paths up to yield; not resumed scheduling |
| [PCM dispatcher predecessor](../audio-early-pcm-dispatch-closure-2026-10-09/REPORT.md) | Buck +5 indirect wrappers |442 comparisons;748 initializer/composition includes608 reused tests; semantic compatibility-name errors explicitly corrected |
| [Correct registry successor](../audio-pcm-registry-interface-successor-2026-10-09/REPORT.md) |4 new wrappers;4 wrappers repeated with correct names |64 comparisons; actual LP-auto entrypoints and recovered children; suspend null only |
| [Mutex task providers](../audio-mutex-disinherit-closure-2026-10-09/REPORT.md) |3 task bodies |711 direct comparisons +24 native queue-give compositions; before-yield boundary |

All receipts were checked against exact final ELF bytes and source/header hashes. PASS is author validation, not independent review or whole-firmware completion. Reused tests and compositions must not be added as unique recovered-function coverage. No production changes, commit, staging or hardware action.

## Concrete leads remaining

- Generic semaphore/mutex take starts0x441C44, ends before0x441DA6. Installed FreeRTOS10.5.1 queue source supplies xQueueSemaphoreTake and private highest-waiter helper (stock0x441EC4). Native inheritance and disinherit providers now exist. Held-count increment0x455AE0 already has exact-source attribution in symbols and public tasks source. This is an actionable bounded source lead; not exhausted or completed here.
- Full common low-power initializer needs actual per-family registration, cached calibration and retention handling composed with already recovered providers. Do not count the sealed variant initializer twice.
- True tempco-suspend wrapper is0x4803DC, registry index10; current stock registration family fixtures leave it empty. Public NO_TEMPSENSE_IN_DEEPSLEEP branch alone does not prove an active stock callback. Live mutation/binding would need runtime trace.
- The selected positive-wait/give paths terminate at a genuine scheduler handover boundary. To establish real lifetime reachability or patch safety, obtain current task PCs, queue/timer/tick/ready state and exception/task scheduling trace or a separately validated scheduler model. Passive PendSV writes are not delivery.

Available source inference is **not globally exhausted**. This ledger preserves a specific next function family rather than claiming all remaining work needs external inputs.
