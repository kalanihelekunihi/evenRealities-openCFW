# G2 CMSIS-FreeRTOS linked-function and commit-boundary census

Status: complete linked-object provenance and functional census; source
admission remains incremental  
Target: official G2 `s200_v2.2.6.10` Apollo-main application  
Scope: read-only firmware/source analysis; no firmware generation or hardware
access

## Result

The G2 image contains one contiguous smart-linked CMSIS-FreeRTOS wrapper
object at `[0x0044900E,0x00449ED2)`. It is 3,780 bytes:

- 43 executable functions / 3,758 bytes;
- 38 public CMSIS-RTOS2 APIs;
- five private wrapper functions (`IRQ_Context`, `TimerCallback`, and the
  three memory-pool free-list helpers); and
- three literal pools / 22 bytes.

All 43 functions are named, bounded, and hashed in
[`cmsis-freertos-v10.5.1-linked-function-map.tsv`](../../tools/manifests/cmsis-freertos-v10.5.1-linked-function-map.tsv).
The complete physical object hashes to
`4213db1407beb89f59deb37d585df874a0fc37939ffb8e16b0f3de2c9c22225a`.
It has 872 direct calls to mapped entries: 831 from outside the object and 41
internal. No external wide or narrow branch enters a function interior. The
only aligned stored entry is the word at `0x00449DD0`, value `0x00449399`,
which installs private `TimerCallback` at `0x00449398`.

This closes the functional identification gap left by the earlier
constructor-only audit. All 38 linked public APIs and all five private helpers
are now production source-owned. See the
[`core-leaf production audit`](cmsis-freertos-core-leaves-source-boundary-audit.md).

## Upstream identity and the proper commit claim

The maintained openCFW selection remains Arm CMSIS-FreeRTOS tag `v10.5.1`:

| Identity | Value |
|---|---|
| annotated tag object | `34e6e4c403c17de35ec0acf29610e374dc938604` |
| peeled tag commit | `d213f261b5be6bb29a7cce8b84071706b72f4d53` |
| tree | `d3689a816acc77a3f0b7d35439d666ad8434b6ba` |
| `cmsis_os2.c` Git blob | `88dca1d881f1a960872572a8a0efd94cde19dcea` |
| `cmsis_os2.c` SHA-256 | `8a0d60b56ad30c4f7957f64fa581158017b6812ec94b832d974c773ae4f2bc36` |
| commit that first introduced that exact source blob | `13acfbef7be85119fc6bc56832c455d4547d92c7` |

The distinction between the last two commits is useful. Commit `13acfbef…`
created the exact 70,106-byte `cmsis_os2.c` blob later shipped by tag commit
`d213f261…`. For reconstruction, use the tagged commit because it also pins
the package descriptor, headers, and declared CMSIS_5 5.9.0 dependency. For
file history or archaeology, `13acfbef…` is the source-producing commit.

The official binary does not prove that Even checked out `d213f261…`
unchanged. It does prove a bounded public behavior interval:

1. Commit `600ba38a66b38105817bd7351be6f6718cd1c2be` introduced three linked
   behaviors together: reject zero-tick `osTimerStart`, return existing plus
   newly set event bits from the `osEventFlagsSet` ISR path, and distinguish
   zero/nonzero ISR timeout in `osEventFlagsWait`.
2. Stock contains all three, excluding tag `v10.4.6` and earlier source.
3. Commit `bb8a350a84567e5a000020abfbd6ab45ea9f6b46` later added a
   re-notification repair to linked `osThreadFlagsWait`. Stock lacks it,
   excluding that commit and later descendants for this function.
4. The intervening `v10.5.1` blob is an exact source oracle. Some commits
   immediately after the tag changed only APIs dead-stripped from G2, so the
   binary cannot collapse the historical checkout to one commit on wrapper
   behavior alone.

The joint evidence is nevertheless strong: the separately authenticated
FreeRTOS Kernel is exactly V10.5.1, CMSIS-FreeRTOS `v10.5.1` packages that
kernel generation and declares CMSIS_5 5.9.0, and all linked wrapper branches
match that source. The correct openCFW dependency pin is therefore
`d213f261…`, while the historical Even checkout remains explicitly
unproven.

## Complete linked families

| Family | Physical span | Functions | Code bytes | Physical bytes | External callers | Linked entries |
|---|---|---:|---:|---:|---:|---|
| kernel management | `[0x0044900E,0x004490E2)` | 5 | 212 | 212 | 148 | `IRQ_Context`, initialize, state, start, tick count |
| threads and thread flags | `[0x004490E2,0x00449376)` | 7 | 660 | 660 | 72 | new, ID, set-priority, yield, terminate, flags-set, flags-wait |
| delay | `[0x00449376,0x00449398)` | 1 | 34 | 34 | 78 | `osDelay` |
| timers | `[0x00449398,0x00449590)` | 6 | 504 | 504 | 60 | callback, new, start, stop, running, delete |
| event flags | `[0x00449590,0x0044971C)` | 4 | 388 | 396 | 38 | new, set, clear, wait |
| mutexes | `[0x0044971C,0x0044989A)` | 4 | 382 | 382 | 325 | new, acquire, release, delete |
| semaphores | `[0x0044989A,0x00449A32)` | 4 | 408 | 408 | 16 | new, acquire, release, count |
| message queues | `[0x00449A32,0x00449C14)` | 6 | 482 | 482 | 89 | new, put, get, capacity, count, delete |
| memory pools | `[0x00449C14,0x00449ED2)` | 6 | 688 | 702 | 5 | new, alloc, free, three private list helpers |

The source-owned public set is `osMutexNew`, `osSemaphoreNew`,
`osMessageQueueNew`, `osKernelGetTickCount`, `osThreadGetId`,
`osMessageQueueGetCapacity`, `osSemaphoreGetCount`,
`osMessageQueueGetCount`, `osMessageQueueDelete`, `osThreadYield`,
`osKernelGetState`, `osMutexDelete`, `osTimerIsRunning`, `osMutexAcquire`,
`osMutexRelease`, `osSemaphoreRelease`, `osTimerNew`, `osTimerStart`,
`osTimerStop`, `osTimerDelete`, `osEventFlagsNew`, `osEventFlagsSet`,
`osEventFlagsClear`, `osEventFlagsWait`, `osMemoryPoolNew`,
`osSemaphoreAcquire`, `osMemoryPoolAlloc`, `osMemoryPoolFree`,
`osMessageQueuePut`, `osMessageQueueGet`, `osDelay`, and
`osThreadSetPriority`, `osThreadTerminate`, `osThreadFlagsSet`,
`osThreadFlagsWait`, `osThreadNew`, `osKernelInitialize`, and `osKernelStart`;
private
`IRQ_Context`, `TimerCallback`, `CreateBlock`, `AllocBlock`, and `FreeBlock`
are also source-owned. Their
entries remain in this map
because the census describes the official stock image and because callers of
those entries are part of the atomic routing contract.

## Explicit dead stripping

The authenticated wrapper exposes 71 public APIs under the recovered compile
configuration. G2 links 38 and dead-strips 33:

`osDelayUntil`, `osEventFlagsDelete`, `osEventFlagsGet`, `osKernelGetInfo`,
`osKernelGetSysTimerCount`, `osKernelGetSysTimerFreq`, `osKernelGetTickFreq`,
`osKernelLock`, `osKernelRestoreLock`, `osKernelUnlock`,
`osMemoryPoolDelete`, `osMemoryPoolGetBlockSize`, `osMemoryPoolGetCapacity`,
`osMemoryPoolGetCount`, `osMemoryPoolGetName`, `osMemoryPoolGetSpace`,
`osMessageQueueGetMsgSize`, `osMessageQueueGetSpace`,
`osMessageQueueReset`, `osMutexGetOwner`, `osSemaphoreDelete`,
`osThreadEnumerate`, `osThreadExit`, `osThreadFlagsClear`,
`osThreadFlagsGet`, `osThreadGetCount`, `osThreadGetName`,
`osThreadGetPriority`, `osThreadGetStackSpace`, `osThreadGetState`,
`osThreadResume`, `osThreadSuspend`, and `osTimerGetName`.

This is useful negative evidence. OpenCFW does not need to reconstruct those
wrapper bodies for stock compatibility unless new source deliberately adds
the APIs.

## Source-admission shortcut and next order

The census changes the next task from discovery to dependency closure. The
highest-leverage source candidates are:

1. `IRQ_Context` plus `osKernelGetTickCount`, `osThreadGetId`, and
   `osMessageQueueGetCapacity` are now production source-owned. Together they
   close 88 stock bytes and 152 external callers without a TCB-field read.
2. `osSemaphoreGetCount` and `osMessageQueueGetCount` are now production
   source-owned. Their identical 36-byte target bodies reuse the source-owned
   normal/ISR queue-count leaves through the shared IRQ helper.
3. `osMessageQueueDelete`, `osThreadYield`, `osKernelGetState`,
   `osMutexDelete`, and `osTimerIsRunning` are now production source-owned
   through already admitted IRQ, scheduler, yield, queue-delete, and timer
   providers.
4. `osMutexAcquire`, `osMutexRelease`, and `osSemaphoreRelease` are also
   production source-owned. Their six unique fixed callees were already
   source-owned, closing 270 stock bytes and 292 external callers.
5. `osTimerStart`, `osTimerStop`, and `osTimerDelete` are production
   source-owned. Their IRQ, timer-command/state/context, and heap-free callees
   were already source-owned, closing 220 stock bytes and 46 external callers.
6. `osEventFlagsNew`, `osEventFlagsSet`, `osEventFlagsClear`, and
   `osEventFlagsWait` are production source-owned. Their constructor,
   task/ISR event-group, and PendSV dependencies were already source-owned,
   closing 388 stock bytes and 38 external callers.
7. `osMessageQueuePut` and `osMessageQueueGet` are now production source-owned
   through complete task/ISR queue send/receive closures. The delay wrapper,
   its FreeRTOS task dependency, and `osThreadSetPriority` plus
   `vTaskPrioritySet` are source-owned too. The next closure admits
   `osThreadTerminate` through source-owned `eTaskGetState`, `prvDeleteTCB`,
   and `vTaskDelete`. The following source-owned thread-flags closure adds the
   three FreeRTOS notification providers plus `osThreadFlagsSet` and the
   pre-`bb8a350a` `osThreadFlagsWait`. The subsequent source-owned
   `osThreadNew` wrapper preserves the G2 static-TCB and 16-bit dynamic-depth
   seams over authenticated retained creators. The final atomic lifecycle
   closure source-owns `osKernelInitialize` and `osKernelStart`, sharing the
   fixed `KernelState` word with source-owned get-state and retaining only the
   authenticated `vTaskStartScheduler` boundary.

The notification closure uses the independently verified 112-byte vendor TCB
layout at `+0x68/+0x6C`; the single-field vendor patch remains explicitly
separate from the authenticated upstream task algorithms.

## Reproduction

Run the read-only analyzer and focused tests:

```sh
python3 openCFW/tools/analyze_g2_cmsis_freertos_linked_census.py
make -C openCFW cmsis-freertos-linked-census
```

The analyzer authenticates the package and vendored source, every function
and literal span, the complete physical-object digest, the 872-call topology,
the sole stored callback, the dead-stripped API set, and the three version
discriminators. It does not write an image or access hardware.
