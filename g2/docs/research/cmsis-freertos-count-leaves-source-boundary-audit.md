# G2 CMSIS-FreeRTOS count-leaf production source boundary

Status: source-integrated in the Apollo-main production overlay  
Target: official G2 `s200_v2.2.6.10`  
Scope: two complete CMSIS-FreeRTOS v10.5.1 entries; offline stock analysis,
host execution, dual-toolchain target builds, and deterministic package assembly

## Result

The second census-ranked CMSIS tranche is now production source-owned:

| Entry | Stock span | Stock bytes | External callers |
|---|---|---:|---:|
| `osSemaphoreGetCount` | `[0x00449A0E,0x00449A32)` | 36 | 1 |
| `osMessageQueueGetCount` | `[0x00449BC8,0x00449BEC)` | 36 | 6 |

Both stock entries implement the same algorithm: reject a null object, use
private `IRQ_Context` to distinguish task and interrupt context, then tail-call
the corresponding FreeRTOS queue-count provider. Complete-entry `B.W` plus
NOP redirects replace all 72 stock bytes. No interior entry, stored pointer,
literal pool, or neighboring function is claimed.

The source is
`components/apollo_main/core_overlay/runtime_cmsis_count_leaves.c`, 3,306
bytes with SHA-256
`cb17116f9e29706cb5e43dc718299d97a41db798b2a02905800266e9f9d285bf`.
It is a bounded Apache-2.0 port of CMSIS-FreeRTOS v10.5.1 `cmsis_os2.c` at
tag commit `d213f261b5be6bb29a7cce8b84071706b72f4d53`; the exact upstream source
blob first appeared at `13acfbef7be85119fc6bc56832c455d4547d92c7`.

## Target and dependency closure

Apple Clang 21 emits a 36-byte unrelocated body for each selector, both with
SHA-256
`dcec0ef689e4b3b991f06fe88e61e48d1b9c7a22862c9758d318db3ce524a0aa`.
Each body has exactly three external relocations:

| Offset | Type | Provider |
|---:|---:|---|
| `+6` | Thumb call | `open_cfw_cmsis_irq_context` |
| `+18` | Thumb jump | `open_cfw_freertos_queue_messages_waiting_from_isr` |
| `+32` | Thumb jump | `open_cfw_freertos_queue_messages_waiting` |

All three providers were already source-owned. The wrapper passes the handle
through unchanged and therefore reads neither Queue_t nor TCB fields. The
recovered 112-byte G2 TCB extension is irrelevant to this tranche.

Host tests cover null, task-context, and ISR-context behavior independently
for both public APIs and prove that exactly one provider is selected. Target
tests authenticate both complete stock spans, the two identical unrelocated
bodies, every relocation, source metadata, and production registration.

## Reproducible outputs

| Profile | Overlay | Apollo-main provider | Core-source package |
|---|---|---|---|
| Apple Clang 21 | 132,116 / `15ebbea5ee6912761f01c8d1dbd45d06f41bf60481c2a8184487814a72793aec` | 3,655,512 / `2e53e625a0a444b5ca9fa74da0de3f730541a1a9b319c27d99aa063b1e29e397` | 4,434,006 / `8276fe0ed7f51336f3640d830c7d74657745e4f31c63ee86d2364bcd006cfa09` |
| Linux Clang 22.1.8 | 133,984 / `e06b60348a96fef23162f57855a37c2fb4f83b921f9d26ef201945154136328b` | 3,657,380 / `27ad96edf82200264bd968b70b3ca7f9be76c5ffe74959c06205f54bf35056bd` | 4,435,874 / `830f12c5dc00bf975b3950dc1f28dfa3b088833a9a60a27d003edbd1b7c87c7e` |

The Apple package accounting is 132,845 source, 93,430 generated, and
4,207,731 opaque bytes. The Linux accounting is 134,865 source, 93,278
generated, and 4,207,731 opaque bytes. No package was signed or flashed and no
hardware was accessed.

## Verification and next boundary

Run:

```sh
make -C openCFW cmsis-freertos-count-leaves
OPENCFW_TOOLCHAIN_PROFILE=apple-clang make -C openCFW core-component
```

At this milestone CMSIS production ownership was eight public APIs plus
private `IRQ_Context`. The subsequent message-queue-delete admission reduces
the stock boundary to 29 public APIs and four private helpers; see
[`cmsis-freertos-message-queue-delete-source-boundary-audit.md`](cmsis-freertos-message-queue-delete-source-boundary-audit.md).
The next useful tier is nonblocking ownership/state queries whose underlying
FreeRTOS providers are already or nearly source-owned. Blocking delay,
acquire, put, and get wrappers should remain behind their kernel/task/queue
provider closures.
