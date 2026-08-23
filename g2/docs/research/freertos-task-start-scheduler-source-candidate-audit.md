# FreeRTOS `vTaskStartScheduler` source-candidate audit

Status: production-routed authenticated MIT source adaptation; offline and
dual-profile complete; hardware timing validation blocked by unavailable
physical evidence

Scope: official G2 `2.2.6.10` Apollo-main application; offline stock/source,
host, and dual-profile target-object verification; no assembly, signing,
flashing, or hardware operation

## Result

The retained scheduler-start entry `[0x00454CEC,0x00454D7C)` is 144 bytes,
SHA-256
`2fabf4882dc6db88c73cd573ba3f454e7f6f0cafb1329670ad52e39ef1cbe01d`.
Its complete control flow is the configured `vTaskStartScheduler()` algorithm
from authenticated FreeRTOS-Kernel V10.5.1 commit
`def7d2df2b0506d3d249334974f51e427c17a41c`.

The bounded adaptation in
`components/shared/freertos/runtime_freertos_task_start_scheduler.c` makes all
G2-specific dependencies explicit instead of treating the full `tasks.c`
translation unit as pristine or ready for production.

## Recovered configuration and behavior

The function uses static allocation for the idle task and timers are enabled.
The application idle-memory hook at `[0x0048D558,0x0048D568)` supplies:

| Item | Value |
|---|---:|
| static idle TCB | `0x20071E30` |
| idle stack | `0x2005F154` |
| stack depth | `0x400` 32-bit words |
| task name | `IDLE` |
| priority | `0` |

It creates the idle task, creates the timer task only after idle success, and
starts the scheduler only after both succeed. The success path masks
interrupts, then writes `xNextTaskUnblockTime=0xFFFFFFFF`,
`xSchedulerRunning=1`, and `xTickCount=0` before entering the Apollo scheduler
port. Timer-task result `-1` reaches the configured fail-stop assertion;
ordinary zero failure returns without changing scheduler globals. The final
volatile `uxTopUsedPriority` read is retained for OpenOCD visibility.

The complete outgoing stock call graph is:

| Call site | Target | Role |
|---:|---:|---|
| `0x00454CFE` | `0x0048D558` | application idle-memory hook |
| `0x00454D1E` | `0x00454820` | `xTaskCreateStatic` |
| `0x00454D34` | `0x0047E674` | `xTimerCreateTimerTask` |
| `0x00454D3C` | `0x005FA0A4` | interrupt mask |
| `0x00454D5A` | `0x004421E2` | Apollo `xPortStartScheduler` |
| `0x00454D6E` | `0x005FA0A4` | assertion interrupt mask |

Its only direct caller is CMSIS `osKernelStart` at `0x004490BE`, which is
already source-owned while deliberately retaining this provider.

## Qualification

The host oracle covers successful creation and write-before-port ordering,
idle creation failure, ordinary timer failure, and timer allocation/assertion
failure. It pins every static-create argument and the state observed at the
port boundary. The stock test pins the full body, sole caller, all six outgoing
calls, all raw word candidates into the function interior, six task-global
literals, the idle hook bytes, and its RAM/depth contract. It also checks the
authenticated upstream source tokens and commit pin.

Apple Clang 21 emits a 2,084-byte object and 156-byte function; Linux Clang
22.1.8 emits a 2,068-byte object and 160-byte function. Both complete object
hashes, function hashes, undefined seams, and all 20 relocations are pinned.
The compiler difference is authenticated and does not change the source or
seam set.

## Production boundary

The scheduler-start chain is production-routed atomically. The overlay binds
the stock idle entry/name, idle handle, four scheduler globals, task/timer
creators, interrupt mask, source-owned `xPortStartScheduler`, and a new
non-returning fail-stop leaf that preserves the stock allocation assertion.
The stock 144-byte entry redirects to a 156-byte Apple leaf (160 bytes under
Linux); strict relocation contracts bind every one of its 20 seams.

The Apple overlay/component/package are 165,412 / 3,688,808 / 4,467,302 bytes
with SHA-256 `91449e27…`, `9b242433…`, and `88e72422…`. The Linux profile is
145,180 / 3,668,576 / 4,447,070 bytes with SHA-256 `afbcb57a…`, `292f5547…`,
and `be5c62a9…`. Both profiles build and package fail-closed.

On-device preemption, stack-overflow-hook, trace concurrency, STIMER latency,
and first-task transfer remain hardware-dependent. The 2026-08-22 hardware
audit found no authorized G2/debug probe/capture path, so this evidence tail is
explicitly blocked; it does not reopen the implemented software row.

Verification:

```sh
make freertos-scheduler-start-core-closure
```
