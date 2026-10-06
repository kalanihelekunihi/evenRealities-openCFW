# Event-waiter removal and missed-yield providers

## Result

`event_waiter_wake.c` reconstructs the stock event waiter remover at
`0x0041872c` and `missed_yield` at `0x004189a2`. The isolated differential
fixture passes **7 removal cases and 3 missed-yield cases**, reaching 314
distinct original instruction bytes. Reproduce with `make test`; raw traces,
per-case memory writes, source hashes, and original function hashes are in
`out/comparison.json`.

The image is `ota_s200_bootloader.bin`, SHA-256
`f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5`.

| Function | Range | Bytes | SHA-256 |
|---|---|---:|---|
| event-waiter remover | `0x0041872c..0x00418822` | 246 | `98a6d87479774e44e46f42c02e98b09f46bf1fc1b1240b6cd172b96625468a06` |
| missed-yield store | `0x004189a2..0x004189ac` | 10 | `86fecf54abdabf46c2e923791f342997647d2d42a74db84fa9207d5756b39d17` |

## Event-removal order and state layout

The input is an event-list header, as used by queue send/receive and timer
queue unlock. Stock reads the first node from `list + 12`, then reads its owner
TCB from `node + 12`. A zero owner takes the fatal path before any list
mutation. The owned item is the TCB event item at `TCB + 24`; the associated
state item is at `TCB + 4` and the ready priority at `TCB + 44`.

First the event node is unlinked from its owner list, repairing the list index
when it points at that node, clearing the node's container, and decrementing
the count. Then the scheduler suspension word at `0x2002716c` selects one of
two paths:

- When not suspended, stock unlinks the state item, raises the highest-ready
  priority at `0x2002714c` if needed, inserts the state item at the tail of the
  priority list selected from `0x20024870 + 20 * priority`, updates the list
  count/container, then refreshes the next-unblock word at `0x20027164` from
  the timer list pointer stored at `0x20027138`.
- When suspended, stock leaves the state item in place and appends the event
  item to the pending-ready list at `0x20026f5c`, updating that list's
  `pxIndex->previous`, links, container, and count.

Finally stock compares the unblocked priority with the current TCB priority
(`current TCB` pointer at `0x20027134`). Only `waiter_priority > current`
sets `0x20027158` and returns 1; otherwise it returns 0. The separate
`0x004189a2` helper always stores 1 to `0x20027158`. Timer queue unlock calls
that helper when the remover returns 1; queue-send/receive paths use the same
return to request rescheduling. This preserves the caller-specific stock
ordering, including timer unlock's duplicate store.

## Source dependencies and validation bounds

The source reuses `opencfw_boot_list_unlink` from `timer_wait.c` for the exact
intrusive list removal and `opencfw_boot_next_unblock_refresh` from
`scheduler_resume.c` for next-unblock recomputation. Its fatal owner path calls
the existing `opencfw_bl_mask_interrupts` provider, then preserves the
stock invalid write to `0xffffffff` and nonreturning loop. No scheduler,
queue, or timer provider outside those helpers is added by this component.

Fixtures compare final memory and ordered SRAM writes for awake, suspended,
equal/higher/lower priority, list-index repair, empty/nonempty timer list, and
null-owner fatal paths. The null-owner case stops at the invalid write before
the intentional infinite loop. The stock remover executes 244 of its 246
bytes across these paths; the two omitted bytes are its terminal self-loop
after the fatal store. The missed-yield function executes all 10 bytes. The
next-unblock helper reaches both empty and nonempty timer-list branches (38 of
46 bytes). All RAM/list/scheduler words are synthetic; no live tasks,
interrupts, queues, timers, or hardware are exercised.
