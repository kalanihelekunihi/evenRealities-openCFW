# Semaphore dependency-source ledger successor

This additive index supersedes the semaphore-take and ISR-semaphore pending rows in earlier ledgers; their sealed history remains unchanged.

| Completed family | Newly exercised bodies | Validation and boundary |
|---|---:|---|
| [Semaphore/mutex take](../audio-semaphore-take-closure-2026-10-09/REPORT.md) |6; held-count increment reused |250 comparisons:107 take,27 highest-waiter,10 reused increment,106 recursive/CMSIS. Genuine port-yield/assertion cuts; no resumed timeout transaction |
| [ISR semaphore/queue](../audio-semaphore-isr-closure-2026-10-09/REPORT.md) |4; copy and wake/port providers reused |392 comparisons, source-only reached instructions; PendSV request only, no delivered exception |
| [Mutex priority providers](../audio-mutex-disinherit-closure-2026-10-09/REPORT.md) |3 |711 direct +24 queue-give compositions; source dependencies reused by new families |
| [Corrected PCM registry](../audio-pcm-registry-interface-successor-2026-10-09/REPORT.md) |4 new,4 repeated |64 comparisons; correct slots and real LP-auto wrappers. True suspend registration stays unproven/zero in family fixtures |

Exact final ELF hashes and all result/source hashes are bound in each batch. Author validation is not independent review, whole-image coverage, source-complete firmware, byte equality or patch safety. Totals include reused comparisons and are not distinct-function coverage sums. Task/list snapshots are constructed and do not prove live reachability. Older queue fixture event values are synthetic inputs, not a claim of actual boot-created task configuration.

## Remaining meaningful leads

1. **CMSIS memory pool**: osMemoryPoolAlloc0x449D3E uses now-native task/ISR semaphore dependencies. Installed public cmsis_os2.c supplies MemPool_t, CreateBlock/AllocBlock/free/reset. Recover actual pool geometry/free-list transitions and bounded allocation/free compositions before claiming pool source closure. This is actionable source inference, not externally blocked.
2. **Scheduler handover**: actual task PCs, tick/queue/ready/owner state and exception trace, or a validated scheduler model, are required for resumed completion and lifecycle safety. Do not passively run through PendSV and label it a task handover.
3. **PCM common low-power initialization**: provider/public source exists, but complete registration/cache/calibration/retention composition remains separate. Existing variant initializer and STIMER accessor are already recovered; do not recapture/count them.

The selected semaphore task/ISR provider source chain is resolved through its tested handover boundary. The whole-project source search is **not exhausted**; this index identifies the next actual function family rather than asserting unavailable inputs block all work.
