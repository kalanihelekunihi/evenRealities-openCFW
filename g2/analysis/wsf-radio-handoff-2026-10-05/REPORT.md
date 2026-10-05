# Radio → WSF event → handler dispatch

Implemented the stock-adapted WSF handoff in `g2/components/foundation/wsf_radio/wsf_radio.c` and a reusable stock-state/provider header. The combined `wsf-radio-simulator` links the actual reconstructed radio/GPIO consumer with WSF event accumulation, critical nesting, wake decision, dispatcher and sleep decision. Its radio scheduler adapter executes WSF logic instead of the previous event-submission fixture. This is a callable foundation increment; RTOS, queues, timers and application handlers remain explicit external providers.

## New understanding

The stock control block at `0x20073230` is64 bytes:10 ARM32 handler pointers at+0;10 byte event masks at+0x28; two padding bytes at+0x32; queue words at+0x34/+0x38; task flags at+0x3c and registration count at+0x3d. The stock initialization/registration instruction chain assigns radio handler ID7 after zero initialization, then stores that byte at `0x20074fcb`. This is static call-chain evidence, not a runtime board observation. The dispatcher uses the actual registered function pointer; this batch does not implement the HCI handler itself.

`WsfSetEvent` selects `handlerId & 15`, ORs the low8 event bits into that byte, ORs4 into task flags, exits its critical section and requests an OS wake. Repeated events coalesce: they are not counted notifications or allocated messages. Zero/high-only event masks still set task-ready and request wake. There is no release-build handler validation: IDs10/11 write padding,12..15 overwrite queue-head bytes. Callers must use initialized handler IDs0..9. Public WSF's default16 handlers/16-bit events cannot be substituted into this layout.

The dispatcher drains message callbacks first and frees each dequeued message afterward; it next handles expired timer messages without invoking message-free; it then handles pending event slots in ascending ID order. Each event byte is captured/cleared before callback. A callback can post to a later ID for service during the same pass; posting to an earlier ID is handled on a subsequent drain pass. A nonzero event whose handler pointer is NULL is left pending even if task flags become zero. Queue/provider ownership and timer-message lifetime beyond these call boundaries are not implemented by the fixture.

WSF critical state is a byte at `0x20075045`. Entry executes CPSID only when nesting was zero, then increments the byte. Exit decrements it and executes CPSIE when it reaches zero. It does **not** restore prior PRIMASK. Balanced depth below255, privileged execution and masked IRQs while already nested are caller requirements; overflow/underflow behavior is not hardened. Tests reproduce nested and wrap-boundary behavior without asserting it safe.

Wake reads task handle `0x20074ef0`. A zero handle produces no OS call. Context classifier result exactly1 selects the ISR provider; other values select the task provider. ISR notification uses `(handle,1,&higher_woken)` and writes PendSVSET `0x10000000` at `0xe000ed04` only when both returned status and higher-woken word are nonzero. Task notification uses `(handle,1)` and, on a nonzero return, writes PendSVSET followed by DSB/ISB. These are recovered raw call conditions, not a claim about every error code or actual scheduler execution. Dispatcher calls timer-update before/after drain and, if ready, invokes the exact five-argument wait boundary `(handle,1,1,0,0xffffffff)`.

## Source and license

Pinned public reference: Packetcraft Cordio r20.05c commit `3656312d6b73e2a2c1c8b33ee0385bc199dd97e6`, Apache-2.0. Four WSF files and LICENSE.md were fetched from that exact commit and checked against pinned Gitblob identities. Arm/Packetcraft copyright and Apache notices are retained, with LICENSE.md delivered in the component. SOURCE_PROVENANCE.json identifies each file/hash and the stock adaptations. The proprietary AmbiqSuite2.5.1 port family is acknowledged using existing repository attribution; no unavailable private source/archive was fetched or claimed exact. The new C is an adaptation/reconstruction, not unchanged upstream text or a byte-identical firmware build.

## Fresh verification

`make -C g2 wsf-radio-simulator` builds the combined callable target; `wsf-radio-simulator-test` executes the new verifier with a fresh output path. `g2/build/foundation/wsf-radio-simulator/comparison-final.json` contains **180 passing original/source comparisons**. Only context/RTOS notification/wait, timer/message providers and application handler fixtures are intercepted. Original WSF critical/event/wake/dispatcher, PendSV write/barriers and radio/GPIO instructions execute; W1C remains synthetic.

Checks compare full event/queue-byte state, depth, PRIMASK, state write width/value/order, MMIO, provider/callback order, message-free calls, mask truncation and ID aliases. Independent models check event coalescing, exact wake decisions, message→timer→handler order, clear-before-callback, self/earlier/later reposts, null handler retention and late timer-update events. The combined disable→pending IRQ→dispatch case retains stock semantics: disabling GPIO117 does not erase its pending status or WSF work. This serialized fixture does not prove a post-disable interrupt occurs on hardware.

All bytes execute across these eight newly explained original bodies:

| Runtime start | Bytes | Function |
| --- | ---: | --- |
| `0x52b8a4` |18| WSF critical enter |
| `0x52b8b6` |18| WSF critical exit |
| `0x52b8d8` |70| OS wake selection |
| `0x52b91e` |64| Set handler event |
| `0x52b95e` |30| Set task-ready flags |
| `0x52b99e` |20| Ready-to-sleep predicate |
| `0x52b9d0` |232| Dispatcher |
| `0x4420bc` |18| PendSV write/barriers |

The comparison observes1110 original bytes including reused functions; **470 are new/disjoint**, bringing cumulative original trace evidence to2364 unique bytes across authenticated payload identities. All470 were unresolved in the initial byte map. The original map and old artifacts are preserved; this increment uses a separate evidence overlay. Foundation inventory now contains28 C/header files and seven callable profiles, with shared helpers counted once. Fully blob-free production payloads remain0/6; no source-built byte-identical bundle is proven.

Fresh foundation tests: **40 passed**. Fresh aggregate: **190 passing methods, zero failures/errors**, six method skips and one class setup skip,35 modules. Independent review found no blocking defect. Firmware, manifest, workflow state and open_cfw.py hashes remain unchanged. No commits, staging, flashing or deployment were performed.

## Limits and next useful increment

There is no physical ISR timing, RTOS scheduling, concurrent producer/dispatcher race proof, shutdown quiescence, allocator lifetime or queue correctness claim. Real HCI application handler code is the next bounded vertical target, followed by its actual queue/transfer provider where evidence supports it. Do not treat GPIO masking as cancellation of WSF work.

A supplemental native WsfOsInit check hit a RAM guard assertion and is explicitly INCONCLUSIVE in init-original-crosscheck.json; it is excluded from passing execution coverage. Static evidence follows the actual shared memset tail beyond an eight-byte function-census prefix. No missing-initialization/no-zero claim is inferred from that prefix, and complete boot/constructor side effects were not tested.

## Evidence navigation

- `original/README.md`, `results-corrected.json`: static identities, layout, registration chain and shared fill-tail correction; earlier snapshots retained as superseded.
- `review/report.md`: independent implementation/instruction-test review.
- `validation-summary.json`, `build-provenance.json`: current validation and hash bindings.
- `cumulative-inventory.json`, `new-code-evidence.jsonl`: disjoint source/target/trace accounting.
- Prior integration: sibling `radio-gpio-consumer-2026-10-05/REPORT.md`; foundational GPIO, critical, CMDQ, MSPI and touch reports remain in their previously delivered sibling directories.
