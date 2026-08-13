# G2 Ring-thread dependency boundary

Status: complete, corpus-independent raw-image closure over the authenticated
G2 2.2.6.10 Apollo payload. This is analysis only and performs no device or
flash operation.

## Result

`platform\threads\thread_ring.c` occupies `[0x004C4CEC,0x004C5734)`:
seventeen functions / 2,374 executable bytes plus a 258-byte literal pool, for
2,632 physical bytes. Ghidra found five functions. Source-order recovery adds
twelve functions, including the actual CMSIS thread entry at `0x004C4CEC`,
queue and lifecycle setup, three retained callbacks, and the record sender.

That first recovery corrects an older ownership error. The BLE Ring-profile
audit had extended its physical interval through `0x004C4D64` even though its
last function ends at `0x004C4C66`. The word at `0x004C5650` is an aligned
Thumb pointer to `0x004C4CEC`, and the target initializes Ring resources before
waiting forever in `osThreadFlagsWait`. The Ring-profile interval is therefore
now `[0x004C46C0,0x004C4CEC)`, 1,580 rather than 1,700 physical bytes. The
120-byte thread entry is admitted exactly once under `thread_ring.c`.

## Dependency result

The 171 direct body calls divide into nine local and 162 external calls:

| Provider | Calls | Provenance |
|---|---:|---|
| EasyLogger | 110 | selected source-equivalent commit `a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24` |
| CMSIS-FreeRTOS | 10 | v10.5.1 commit `d213f261b5be6bb29a7cce8b84071706b72f4d53` over FreeRTOS-Kernel `def7d2df2b0506d3d249334974f51e427c17a41c` and CMSIS_5 `2b7495b8535bdcb306dac29b9ded4cfb679d7e5c` |
| FreeRTOS assert port | 2 | separately bounded fail-stop seam at `0x005FA0A4` |
| IAR DLIB | 2 | one `memcpy`, one `memset`; proprietary runtime remains bounded |
| TLSF-backed heap wrappers | 3 | production-owned wrappers over selected TLSF `deff9ab509341f264addbd3c8ada533678591905` |
| closed Ring service | 13 | first-party touch, pair, discovery, connection, heartbeat, reconnect, and advertising policy |
| G2 event-loop providers | 16 | delayed-event schedule/remove seam |
| other first-party providers | 6 | connection state and thread lifecycle registration |

The exact CMSIS calls are `osThreadNew`, `osThreadTerminate`,
`osThreadFlagsSet`, `osThreadFlagsWait`, `osDelay`, `osMessageQueueNew`,
`osMessageQueuePut`, `osMessageQueueGet`, and `osMessageQueueDelete`. They use
already authenticated source bodies and add no new FreeRTOS version or commit
discriminator.

There is no hidden Cordio, Ring protocol, allocator, or scheduler
implementation in this object. Ring policy remains first-party, while all
reusable utilities terminate at already selected providers. The private G2
producing commit is therefore still binary-unobservable.

## Ingress and behavior closure

The object has 21 direct `BL` entry sites, eight stored Thumb entry pointers,
zero indirect body calls, and zero strict-interior ingress. The stored pointers
include the thread descriptor, three touch callbacks, pair callback, and public
message/event entries. Twenty-two raw path references occur in nine functions;
the authenticated Ghidra census conservatively counts five path anchors.

Recovered behavior covers the complete lifecycle: a three-entry/four-byte
CMSIS queue, flag-driven dispatch, touch and pairing policy, Ring-service
discovery/connection events, delayed heartbeat/reconnect/advertising work, and
bounded record allocation/free.

## Reproduction

```sh
python3 openCFW/tools/analyze_g2_thread_ring.py
python3 -m unittest openCFW.tests.test_analyze_g2_thread_ring
```

The analyzer pins every function body, the complete physical interval and
literal pool, all call and ingress topology, the corrected preceding object
boundary, retained-path references, provider commits, and production-overlay
exclusion.
