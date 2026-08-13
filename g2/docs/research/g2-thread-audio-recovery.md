# G2 audio-thread recovery

Status: complete linked-object and provider closure over the authenticated G2
2.2.6.10 Apollo image. This is read-only analysis; it performs no device or
flash operation and does not route the reconstructed object into production.

## Result

The three Ghidra path anchors for
`platform\threads\thread_audio.c` account for only 394 bytes. Raw literal
recovery shows that the same retained path is referenced 24 times from 13
functions and that the complete contiguous object is
`[0x0053C2BE,0x0053CF78)`: 31 functions / 2,954 body bytes, 302 bytes in three
outer pools, and one two-byte alignment gap, for 3,258 physical bytes.

The authenticated baseline discovered 12 of those functions. Nineteen restored
bodies include thread/resource initialization, timer control, the thread entry,
PDM and codec handlers, the audio watchdog, voice-event policy, peer sync, and
exit. The closure pins all 1,101 reachable instructions, 203 direct body calls,
43 whole-image direct BL entries, three stored Thumb entry pointers, all path
references, both physical boundaries, and the single register-indirect message
dispatch at `0x0053C5E0`. No BL reaches a strict function interior.

## Third-party boundary and source shortcuts

The object embeds no third-party definition. Its reusable edges are already
source-owned or bounded:

| Provider | Edges | Source identity |
|---|---:|---|
| EasyLogger | 120 direct | 2.2.99-compatible core, selected commit `a596b264…` |
| CMSIS-FreeRTOS | 20 direct / 14 wrappers | v10.5.1 selected commit `d213f261…` |
| IAR DLIB | 1 direct | bounded four-byte `memset`; EWARM 9.20+ floor, 9.60.2 leading candidate |
| Closed codec/GX8002B objects | 19 direct | composes the recovered codec DFU, codec host, and GX8002B objects |
| Other first-party audio/input/callback policy | 23 direct + 1 indirect | private Even source, provider seams identified |

The 14 CMSIS wrappers are `osKernelGetTickCount`, `osThreadNew`,
`osThreadTerminate`, `osThreadFlagsSet`, `osThreadFlagsWait`, `osDelay`, timer
new/start/stop/delete, and message-queue new/put/get/delete. The wrapper source
is pinned to CMSIS-FreeRTOS v10.5.1 commit
`d213f261b5be6bb29a7cce8b84071706b72f4d53`; its selected FreeRTOS-Kernel is
V10.5.1 commit `def7d2df2b0506d3d249334974f51e427c17a41c`, and the selected CMSIS_5
header dependency is 5.9.0 commit
`2b7495b8535bdcb306dac29b9ded4cfb679d7e5c`. This consumer supplies broad
independent confirmation of those admitted sources but no new historical
commit discriminator.

The 19 already closed audio calls are especially useful for OpenCFW: two enter
the codec-DFU object, seven enter the GX8002B/I2S driver, and ten enter the
codec-host service. Consequently the object does not pull NationalChip LVP
firmware or another host library into Apollo flash. Device-side GX8002B
firmware/tooling remains an external dependency, not linked source.

## Recovered behavioral contract

The resource initializer creates a 50-entry queue of 12-byte messages and a
2,000-tick codec-activity watchdog. The dispatcher recognizes eight message
IDs through a runtime first-party callback table. DMA notifications are
accepted when their recorded tick is at most 40 ticks old. The watchdog treats
fewer than 20 codec events per interval as failure and requests a codec restart.

The only indirect call loads one of eight runtime callback slots rooted at
`0x20003FBC`; the call site and table bounds are pinned, but the callbacks are
first-party runtime registrations rather than a linked utility library. The
thread exits by unregistering callbacks, stopping/deleting its timer, deleting
the queue, logging completion, and entering an infinite delay loop.

## OpenCFW consequence

There is no remaining third-party functional gap in this object. Reuse the
admitted CMSIS-FreeRTOS, EasyLogger, and bounded DLIB implementations, plus the
existing codec/GX8002B object contracts. Remaining work is first-party message,
role, PDM, GPIO, voice-event, and lifecycle reconstruction followed by hardware
validation of DMA timing, codec restart behavior, and shutdown ordering.

Reproduce with:

```sh
make thread-audio-closure
```
