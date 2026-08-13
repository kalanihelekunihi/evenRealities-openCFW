# G2 Cordio/Ambiq FreeRTOS WSF OS and queue recovery

Status: production-excluded source recovery. The official firmware and the
authenticated 64-shard Ghidra corpus are read only. No production overlay,
package manifest, firmware byte, or hardware state changed.

## Result

The complete WSF OS cluster is `[0x0052B8A4,0x0052BAB8)`, 532 bytes,
SHA-256 `7ed04ab36ab918395ca59c417aaff620aa2777d8721720efc123a0cc729fb408`.
The linked intrusive-queue cluster is `[0x00538C24,0x00538D16)`, 242 bytes,
SHA-256 `a1288313d8580bb67c5d5dc23170f4484dbac464db2cb754293545547f26c0a9`.
All 18 bounded functions have named boundaries, authenticated body hashes,
caller/callee closure, and production-excluded clean-room behavioral source.

| Module | Bounded functions | Stock bytes | Recreated state |
|---|---:|---:|---|
| `wsf_os.c` | 12 | 532 | Complete behavioral candidate; production-excluded |
| `wsf_queue.c` | 6 | 242 | Complete linked-body candidate; production-excluded |
| Queue API beyond linked stock | 1 | 0 | `WsfQueueEmpty` source behavior only; no bounded stock body |

The OS functions are `WsfCsEnter`, `WsfCsExit`, `WsfTaskLock`,
`WsfTaskUnlock`, `WsfSetOsSpecificEvent`, `WsfSetEvent`, `WsfTaskSetReady`,
`WsfTaskMsgQueue`, `WsfOsSetNextHandler`, `wsfOsReadyToSleep`, `WsfOsInit`,
and `wsfOsDispatcher`. The six linked queue bodies are `WsfQueueEnq`,
`WsfQueueDeq`, `WsfQueuePush`, `WsfQueueInsert`, `WsfQueueRemove`, and
`WsfQueueCount`. The two-byte range `[0x00538D16,0x00538D18)` is alignment;
unrelated code starts at `0x00538D18`.

An exhaustive direct-BL scan closes all callers, including 13 callers of
`WsfCsEnter`, 14 of `WsfCsExit`, 28 of `WsfTaskLock`, 29 of
`WsfTaskUnlock`, and the single dispatcher caller at `0x004D0A62`. Queue
callers close at three enqueue, three dequeue, one push, two insert, two
remove, and two count sites. All expected outgoing calls are decoded at their
exact instruction addresses. A full aligned raw-pointer scan finds no stored
entry or interior pointer for either cluster. No production relocation or
placement is claimed yet.

Unlike the adjacent retained `wsf_timer.c` path, the stock image does not
retain a `wsf_os.c` or `wsf_queue.c` `__FILE__` anchor. Their identity rests
on source order, function semantics, ABI, constants, direct-call topology,
and two independent release/configuration discriminators. This distinction is
kept explicit by the analyzer.

## Source lineage and license boundary

The official AmbiqSuite 2.5.1 S3 archive is 200,161,418 bytes, SHA-256
`87b03680c0ac5a5291938e7c522f86146a954d935588f1deb046f35012fe4133`.
Its `third_party/cordio/wsf/sources/port/freertos/wsf_os.c` is 11,665 bytes,
SHA-256 `892a7ae0283ba9274f80e48e6a2507cf49d3075fad7c3298656afc98a1a56e4a`,
Git blob `8a466f57d90e402502cdfcfda96e616736487021`. The queue source is 8,650
bytes, SHA-256
`7dd109b4509d31c3222827b73f7ed5587e46a2c9d2de54ed8f30c599d418cf86`,
Git blob `7eab0ae7d02486a9e8af9419cc8f25235a2a1200`.

The 2.4.2 OS source differs at the dispatcher tail: it waits
unconditionally and lacks the second `WsfTimerUpdateTicks()` plus
`wsfOsReadyToSleep()` guard. Stock has the 2.5.1 behavior. The queue source is
byte-identical across 2.4.2, 2.5.1, and the later official Ambiq R4.4.1
source copy, so queue identity is selected jointly with the OS/timer release
discriminators rather than treated as a point-release discriminator itself.

AmbiqSuite 2.5.1 defaults `WSF_MAX_HANDLERS` to 9, while the stock binary
mechanically proves an effective value of 10. The exact G2 definition site is
unavailable; it must not be described as a proven command-line override.
Later official Ambiq source provides the missing corroboration:

- AmbiqAI/neuralSPOT commit
  `4264b9309e03064ffad13a0468d5d0c1110c5288`, labeled R4.4.1;
- AmbiqAI/nsx-ambiq-sdk commit
  `9f36432d875060ca301675131b40452ecf8377ca`.

Both carry `wsf_os.c` blob `c37a11641314c53d30d8051937f4c808acc71cfb`,
SHA-256 `9a3e95310d78bbaea55dc62b7e0bd22bb6db764afd2822877e3e4ceeeab7d2ff`.
It differs from the authenticated 2.5.1 source by one byte/line only: the
guarded default changes from 9 to 10. These later imports corroborate the
stock-effective source variant; they are not historical G2 commit pins.

Both original source files carry file-specific proprietary Wicentric/ARM
license headers. OpenCFW records archive, file, line-span, and Git-blob
identities without redistributing those sources. The maintained candidate is
an independently expressed clean-room behavioral reconstruction.

## Recovered ABI and memory layout

The 20-byte literal table `[0x0052BAB8,0x0052BACC)` has SHA-256
`3806c76818681d6c5562202b5458198dbcd6d50f5653793814cadafaca6d73ff`
and decodes to:

| Address/value | Meaning | State |
|---|---|---|
| `0x20075045` | 8-bit critical-section nesting counter | Fully decoded |
| `0x20074EF0` | FreeRTOS event-group handle | Fully decoded |
| `0xE000ED04` | SCB ICSR; direct PendSV-set write | Fully decoded |
| `0x20073230` | WSF OS task object | Fully decoded |
| `0x20073264` | Embedded message queue | Fully decoded |

The stock task object is exactly 64 bytes:

| Offset | Field |
|---:|---|
| `+0x00` | ten 32-bit handler pointers |
| `+0x28` | ten 8-bit handler-event masks |
| `+0x32` | two bytes padding |
| `+0x34` | message queue head |
| `+0x38` | message queue tail |
| `+0x3C` | 8-bit task-event mask |
| `+0x3D` | 8-bit registered-handler count |
| `+0x3E` | two bytes padding |

Task event bits are message queue `1`, timer `2`, and handler `4`. The generic
queue is eight bytes (`head +0`, `tail +4`), and every element begins with its
next pointer. `WsfQueueInsert` deliberately nests queue critical sections;
the byte nesting counter makes that behavior safe. First CS entry emits
interrupt disable and final exit emits interrupt enable, with the stock
8-bit wrap/underflow behavior preserved.

The dispatcher updates timer ticks, snapshots and clears the task mask under
the CS, drains normal messages before expired timers before handler-event
masks, repeats when callbacks post more work, updates ticks again, and waits
on event bit 1 only when ready to sleep. In an ISR wake path, stock directly
writes `0x10000000` to ICSR after a successful event-set that wakes a higher
priority task; the clean-room candidate exposes this as a narrow explicit
PendSV seam rather than an extra yield call.

## Clean-room candidate and validation

The candidate files are:

- `runtime_cordio_wsf_os_candidate.c`, 6,733 bytes, SHA-256
  `fd754f3323b5c97e7d61961757eb55d7f6aec4238949ab6e86cc8b77f62f95be`;
- `runtime_cordio_wsf_os_candidate.h`, 4,368 bytes, SHA-256
  `4811e2683a356cef52f163535e457398d7eb2dae1079d2047fbf8c29a03c43b9`;
- `runtime_cordio_wsf_queue_candidate.c`, 3,648 bytes, SHA-256
  `e04c1483b245ce8cc94aaaefa1a1187b5f049e5f39afeeb66caf1da5b8cbbf11`;
- `runtime_cordio_wsf_queue_candidate.h`, 1,871 bytes, SHA-256
  `9c39532c9c9ed424c0db00ced5d8522501ce3fd08bcfac4e69ff4aeebd14fcc7`.

The timer, OS, and queue headers now share one generic queue ABI and one set
of WSF lock/ready symbols. A mandatory `arm-none-eabi` Clang compile gate
builds all three modules with `-Wall -Wextra -Werror` and exercises target-only
layout assertions. The host harness covers queue head/middle/tail operations,
preserved removed-next behavior, nested locks, CS underflow, null/ISR/task wake
paths, direct PendSV semantics, initialization, registration, queue identity,
message/timer/handler dispatch priority, callback arguments, message-only
freeing, two timer updates, and exact event-wait arguments.

`tools/analyze_g2_cordio_wsf_os.py` fails closed on the official image,
all 133 authenticated Ghidra-corpus files, both module spans, all 18 body
hashes, every enumerated caller/callee, the literal/global table, candidate
hashes, provenance ledgers, and Lorelei matrix summaries. Its tests leave the
candidates absent from every production overlay and manifest.

## Lorelei stock-ABI matrix

The returned compact artifact is repository-owned at
`research/readiness/wsf-os-queue-stockabi/`, 26,090 bytes,
SHA-256 `41dfe210be05c9ba4455353d5c6bc047eb775e1d1e8aba105c6dcf91c83ccdbd`.
Its checksum manifest authenticates 20 files and deliberately excludes
proprietary source and generated objects.

Lorelei compiled 13 explicit GCC 13.2.1 configurations for both translation
units, linked 13 closure ELFs, and compared 234 function/config rows in
**3.521196588 seconds**. Every source/stub compile passed `-Werror`, and every
linked lane had zero unresolved symbols. There were zero raw and zero strict
address/relocation/call/branch-normalized matches. `-Os` with sibling-call
optimization disabled was the best common OS/queue profile: 4/18 exact-size
functions and aggregate absolute size delta 74 bytes. Bounded per-function
selection made six functions size-exact: the lock/unlock wrappers,
ready-to-sleep, dequeue, remove, and count. Size equality is structural
evidence only and does not prove IAR source/compiler identity.

## Completeness estimate and next tranche

The bounded OS and linked-queue tranche is **95–98% semantically and
source-family identified**: 774/774 code bytes have names, body hashes,
call topology, ABI, upstream-family mappings, and tested clean-room behavior.
The remaining 2–5% is the exact historical 10-handler definition site, local
text/configuration drift, IAR code generation, production relocation and
placement, and target verification. `WsfQueueEmpty` remains explicitly outside
stock-byte coverage.

Overall Packetcraft/Ambiq Cordio remains **80–85% identified** because the
wider HCI, trace, buffer, message, application, and vendor-port boundaries are
not yet closed. The highest-value next tranche is `wsf_buf.c`, whose exact
FreeRTOS-port path is retained and whose stable Ambiq source blob is already
authenticated; `wsf_msg.c` follows because it closes the dispatcher message
providers. Package byte ownership does not change: these research candidates
remain production-excluded, and the opaque/cut-forward package share remains
94.920289%.
