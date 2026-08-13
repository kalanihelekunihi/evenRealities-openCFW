# G2 CMSIS-FreeRTOS core-leaf production source boundary

Status: source-integrated in the Apollo-main production overlay  
Target: official G2 `s200_v2.2.6.10`  
Scope: four complete CMSIS-FreeRTOS v10.5.1 entries; offline analysis, host
execution, dual-toolchain target builds, and deterministic package assembly

## Result

Four high-leverage entries from the authenticated 43-function stock wrapper
object are now production source-owned:

| Entry | Stock span | Stock bytes | External callers | Source dependency |
|---|---|---:|---:|---|
| private `IRQ_Context` | `[0x0044900E,0x0044903C)` | 46 | 0 external / shared by linked wrappers | source-owned `xTaskGetSchedulerState` |
| `osKernelGetTickCount` | `[0x004490CC,0x004490E2)` | 22 | 144 | source-owned IRQ helper and both tick getters |
| `osThreadGetId` | `[0x004491AA,0x004491B2)` | 8 | 6 | source-owned opaque current-task getter |
| `osMessageQueueGetCapacity` | `[0x00449BBC,0x00449BC8)` | 12 | 2 | authenticated `Queue_t.uxLength` at `+0x3C` |

The stock tranche totals 88 bytes. Each complete entry is replaced by one
generated `B.W` plus NOP fill; no interior entry, stored pointer, literal pool,
or neighboring function is claimed. The appended source tranche is 84 code
bytes plus four alignment bytes.

The source is
`components/apollo_main/core_overlay/runtime_cmsis_core_leaves.c`. It is a
bounded Apache-2.0 port of the exact CMSIS-FreeRTOS v10.5.1 `cmsis_os2.c`
selected at commit `d213f261b5be6bb29a7cce8b84071706b72f4d53`; that exact
source blob first appeared at
`13acfbef7be85119fc6bc56832c455d4547d92c7`.

## Why the leaves are independent of the vendor TCB

`IRQ_Context` reads Cortex-M `IPSR`, and—after the scheduler starts—`PRIMASK`
and `BASEPRI`. Its sole call is the already integrated scheduler-state getter.
The scheduler-not-started branch deliberately ignores mask state, matching the
upstream and stock policy.

`osKernelGetTickCount` chooses the normal or ISR FreeRTOS tick getter through
that helper. Both getters already close over the atomic G2 `xTickCount` word at
`0x20074A34`.

`osThreadGetId` forwards `xTaskGetCurrentTaskHandle`. The provider returns the
opaque `pxCurrentTCB` word at `0x20074A20` without dereferencing it.

`osMessageQueueGetCapacity` returns zero for a null queue or reads the 32-bit
`uxLength` word at Queue_t offset `0x3C`. The offset is independently bounded
by the source-owned FreeRTOS queue creators and the adjacent
`uxMessagesWaiting` word at `0x38`.

Consequently, none of the four leaves reads a TCB field, depends on the G2
112-byte TCB size, migrates kernel RAM, or introduces a hardware port.

## Target outputs and dependency closure

Apple Clang 21 emits the following independently extracted leaves:

| Source function | Code bytes | Outgoing relocations |
|---|---:|---|
| `open_cfw_cmsis_irq_context` | 46 | scheduler-state `BL` |
| `open_cfw_cmsis_kernel_get_tick_count` | 24 | IRQ `BL`; normal/ISR tick tail branches |
| `open_cfw_cmsis_thread_get_id` | 4 | current-task tail branch |
| `open_cfw_cmsis_message_queue_get_capacity` | 10 | none |

The same unrelocated function bytes compile under Homebrew Clang 22.1.8.
Profile-specific final hashes differ only where relocation displacement changes.
Both reviewed profiles build and authenticate complete packages:

| Profile | Overlay | Final Apollo provider |
|---|---|
| Apple Clang 21 | 132,042 bytes / `471959546891f1c59d1f6f5e05606a64da3bd5d1eed9df4608d513b5e5b3946d` | 3,655,438 bytes / `7175f0b05ecde3d71641ca37b1fa2c92d152faa660f985aa373c1da5367d1788` |
| Linux Clang 22.1.8 | 133,910 bytes / `a5f25988c06f6a76b101c4739addfeac5db397076b89705b45091a1818eb386a` | 3,657,306 bytes / `1d3f9c4d6842e0a8c25971c51f1aafbfea8568ddb4a6b2da333d2e92d3bc6eb6` |

The canonical core-source EVENOTA is 4,433,932 bytes with SHA-256
`01f8c3acffb69a9edf6bdaadc6c41d11cbf61ed8e716ab8278a4da8e778f4418`.
No package was signed or flashed and no hardware was accessed.

## Verification

`tests/test_runtime_cmsis_core_leaves.py` authenticates the source snapshot and
all four stock spans, host-executes interrupt/mask and provider selection,
proves the opaque handle and Queue_t offset behavior, pins each target section
and relocation, and checks production overlay/manifest registration.

Run:

```sh
python3 -m unittest -v openCFW.tests.test_runtime_cmsis_core_leaves
OPENCFW_TOOLCHAIN_PROFILE=apple-clang make -C openCFW core-component
```

At this milestone the remaining linked CMSIS stock boundary was 32 public APIs
and four private helpers. The subsequently integrated semaphore/message-queue
count tranche reduces that boundary to 30 public APIs and four private helpers;
see
[`cmsis-freertos-count-leaves-source-boundary-audit.md`](cmsis-freertos-count-leaves-source-boundary-audit.md).
Blocking delay, acquire, put, and get paths should continue to wait for their
underlying FreeRTOS task/queue providers.
