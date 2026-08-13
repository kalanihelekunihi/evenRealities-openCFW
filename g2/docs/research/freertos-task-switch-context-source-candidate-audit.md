# FreeRTOS `vTaskSwitchContext` source-candidate audit

Status: production-excluded G2 source candidate; target integration and
hardware scheduling validation remain mandatory

## Result

The complete stock `vTaskSwitchContext` body
`[0x004551B4,0x00455282)` is 206 bytes with SHA-256
`fe979ce2eed1eeac9ca5c54192d428ef98825775f1665113ccbe0caf302c7343`.
Its scheduler control flow is the generic task-selection implementation in
FreeRTOS-Kernel V10.5.1 `tasks.c`, authenticated at annotated tag `V10.5.1`,
peeled commit `def7d2df2b0506d3d249334974f51e427c17a41c`, tree
`7496dfa815c3cea2f45a090c6e92d113f494b930`.

The G2 build adds two configuration/vendor seams around that upstream body:

- method-2 stack-overflow checking reads four `0xA5A5A5A5` words from the
  stack base at TCB `+0x30` and calls the first-party hook at `0x0046D86C`
  with the TCB and its name at `+0x34`; and
- custom `traceTASK_SWITCHED_OUT/IN` hooks store the old/new TCB number from
  `+0x58` in an external 64-entry, eight-byte trace ring at `0x2006F348`,
  indexed by the wrapping word at `0x20074A5C`.

## Exact stock topology

The only direct callers are the nominally unreachable tail of
`xPortStartScheduler` at `0x00442204` and `PendSV_Handler` at `0x005FA0F6`.
The only outgoing calls are:

| Call site | Target | Role |
|---:|---:|---|
| `0x004551FC` | `0x0046D86C` | G2 stack-overflow hook |
| `0x00455230` | `0x005FA0A4` | assertion interrupt mask |

The fixed global/literal seams are:

| Literal site | Value | Meaning |
|---:|---:|---|
| `0x00455468` | `0x20074A58` | `uxSchedulerSuspended` |
| `0x00455A14` | `0x20074A44` | `xYieldPending` |
| `0x00455C34` | `0x20074A20` | `pxCurrentTCB` |
| `0x00455C38` | `0x20074A5C` | G2 trace index |
| `0x00455C3C` | `0x2006F348` | G2 trace ring |
| `0x00455C40` | `0x20074A38` | `uxTopReadyPriority` |
| `0x00455DBC` | `0x2006A49C` | 56-element ready-list array |

Byte-granular whole-image scanning finds 13 false interior word candidates;
none is a stored entry pointer. The test pins their exact locations and
values so future boundary drift fails closed.

## Recovered behavior

When scheduling is suspended the function only sets `xYieldPending=1`. In the
normal path it clears that word, checks the outgoing task's four stack guard
words, records the outgoing task number, and scans down from
`uxTopReadyPriority` until it finds a nonempty ready list. Zero priority with
an empty list takes the stock assertion fail-stop.

The generic list selector advances `List_t.pxIndex`, skips the embedded end
sentinel, loads the selected item's owner as `pxCurrentTCB`, and publishes the
selected priority. It then records the incoming task number, increments the
trace index, and wraps it to zero at 64. This confirms
`configUSE_PORT_OPTIMISED_TASK_SELECTION=0`,
`configCHECK_FOR_STACK_OVERFLOW>1`, and the already recovered 20-byte
`List_t`/112-byte G2 TCB layouts.

## Qualification

The deterministic host oracle covers the suspended path, priority descent,
sentinel skipping, multi-task round robin, every one of the four stack guard
words, trace ordering/wrap, and the empty-priority assertion seam. Stock tests
pin the body, both callers, both outgoing calls, all literal words, and all
false interior candidates.

Apple Clang 21.0.0 emits a 1,364-byte object with SHA-256
`4fedef033dc94ab8a9862be504795421daafaa0bbc683526108e8dc4554d763f`;
its 266-byte function body has SHA-256
`37bfb94e9294e10861e68f6e191e12db2be17cef97a412e15a2857fa32874c0b`.
Linux Clang 22.1.8 emits 1,344 bytes with SHA-256
`abcef8aada535b4c8aba7367039b79bedd9b4d581ad353567901996021545eb4`;
its 266-byte body has SHA-256
`d5d43e9359c06270e28900321583ac9663caf9191becd82de54985e085c2b5f8`.
Both have only the expected stack-hook and assertion-mask call relocations.

## Boundary

The candidate is deliberately absent from every production manifest and
Makefile input. It closes the bounded scheduler-selection and custom trace
algorithms, but it does not authorize replacement of the live scheduler.
Production admission still requires an atomic kernel/port integration and
on-device preemption, overflow-hook, and trace-concurrency validation.

Verification:

```sh
python3 -m unittest -v tests.test_runtime_freertos_task_switch_context
```
