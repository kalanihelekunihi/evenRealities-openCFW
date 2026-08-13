# G2 thread-pool dependency boundary

Status: complete, corpus-independent raw-image closure over the authenticated
G2 2.2.6.10 Apollo payload. This is analysis only and performs no device or
flash operation.

## Result

`framework\sync\thread_pool.c` occupies `[0x0049110C,0x004916B8)`: three
functions / 1,290 executable bytes plus a 162-byte trailing literal pool, for
1,452 physical bytes. Ghidra found the two path-anchored functions
`0x00491184` (pool creation) and `0x0049137A` (job submission). Source-order
recovery adds the worker-thread entry at `0x0049110C`, which Ghidra missed;
it is admitted by the stored Thumb pointer at `0x0049169C` inside the object's
own literal pool (the creation function passes it to `osThreadNew`) and by its
direct `osMessageQueueGet` dispatch loop with retained-path logging
(12 raw references to the path cell `0x00491624`).

The preceding boundary is a two-byte alignment pad (`movs r0,r0` at
`0x0049110A`) after the unowned path-less block that ends at `0x00491109`; no
retained path, call edge, or stored pointer ties that block to this object.
The following boundary is the 16-byte memset helper `0x004916B8`, called only
from TinyFrame code at `0x004919F0`; it belongs to the TinyFrame tranche that
starts at `0x004916C8` (`third_party\TinyFrame\TinyFrame.c`).

## Dependency result

All 78 direct body calls leave the object; there are zero internal direct
calls (the worker entry is reached through the pool-stored pointer, not `BL`):

| Provider | Calls | Provenance |
|---|---:|---|
| EasyLogger | 60 | selected source-equivalent commit `a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24` |
| CMSIS-FreeRTOS | 10 | v10.5.1 commit `d213f261b5be6bb29a7cce8b84071706b72f4d53` over FreeRTOS-Kernel `def7d2df2b0506d3d249334974f51e427c17a41c` and CMSIS_5 `2b7495b8535bdcb306dac29b9ded4cfb679d7e5c` |
| IAR DLIB | 6 | aligned-copy/fill/`snprintf` and the bounded wait seam; EWARM 9.20+ floor, 9.60.2 leading candidate |
| FreeRTOS assert port | 2 | bounded fail-stop seam at `0x005FA0A4` |

The exact CMSIS seams are `osThreadNew`, `osMutexNew`, `osMutexAcquire`,
`osMutexRelease`, `osMutexDelete`, `osMessageQueueNew`, `osMessageQueuePut`,
`osMessageQueueGet`, and `osMessageQueueDelete`. They use already
authenticated source bodies and add no new FreeRTOS version or commit
discriminator. There is no first-party call edge: the pool depends only on
selected third-party providers and the bounded IAR runtime.

The single indirect call at `0x00491180` is the job callback: the worker loop
loads the callback pointer and its argument from the dequeued 24-byte job
record (`ldr r4,[sp,#0xc]` ... `blx r4`) and repeats. It is bounded to
records submitted through the anchored submission function.

## Ingress and behavior closure

The object has 18 direct `BL` entry sites (17 into the creation function,
one into the submission function from the closed `sync_framework.c` region),
one stored Thumb entry pointer (`0x0049169C -> 0x0049110C` in its own pool),
zero wide-branch entries, zero strict-interior targets, and zero noncode `BL`
targets. One raw instruction-aligned 32-bit window at `0x00585C31` spells
`0x004915D1` inside the submission function; it is a data coincidence, not a
stored pointer.

The trailing 162-byte pool `[0x00491616,0x004916B8)` holds the retained-path
cell, the worker-entry pointer cell, queue/mutex/thread attribute literals,
and format-string pointers.

## Discriminator evidence and limitations

No embedded reusable third-party body exists in this object; there is no
hidden scheduler, allocator, or queue implementation beyond the admitted
CMSIS-FreeRTOS seams. The private G2 producing commit remains
binary-unobservable. The unowned 7.7 KB path-less block at
`[0x0048F3BE,0x0049110A)` is explicitly not claimed; it shares no call,
pointer, or path evidence with `thread_pool.c`.

## Reproduction

```sh
python3 openCFW/tools/analyze_g2_thread_pool.py
python3 -m unittest openCFW.tests.test_analyze_g2_thread_pool
```

The analyzer pins every function body, the complete physical interval and
literal pool, all call and ingress topology, both object boundaries, the
retained-path references, provider commits, and production-overlay exclusion.
