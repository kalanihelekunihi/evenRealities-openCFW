# Notification wait: ready-list removal and block insertion

**704 original/source comparisons PASS** against the locked main image and the
final native ELF. [Reconstructed insertion](../../components/audio/notification_block_offline/block.c),
[interface](../../components/audio/notification_block_offline/block.h),
[full cases](results.json), and [build receipt](reproduction-receipt.json).

Stock `0x455FA8` removes the current task's state item from its ready list. For
finite ticks it stores `deadline = current_tick + ticks`, inserts into the
overflow delayed list when unsigned addition wraps, otherwise inserts into the
current delayed list and lowers `next_unblock` only when needed. The special
`ticks == 0xFFFFFFFF && can_block_indefinitely != 0` path inserts at the end of
the separate suspended list and does not update `next_unblock`.

The list insertion is sorted and stable relative to existing deadlines. The
tests vary tick `0`, `100`, `FFFFFFFE`, `FFFFFFFF`; wait `0`, `1`, `2`, `5`,
`FFFFFFFF`; infinite-wait flag; an existing ready peer; existing current and
overflow deadlines; and whether the ready-list index points at the current
task. All selected task/list/global writes occur under `BASEPRI=0x30`.

The same insertion is executed through notify-wait `0x455B84` for states
0/1/2 and timeout `0/1/2/FFFFFFFF`. A pending notification (state2) bypasses
blocking. A positive wait with no pending notification marks state1, performs
the recovered insertion, then stops before yield `0x4420BC`. No PendSV write,
exception delivery, timeout, notification arrival, resumed return, or bit
clearing after wake is synthesized. Zero-timeout paths complete through the
real critical helpers and restore `BASEPRI=0`.

Fixtures use coherent synthetic TCB and list state. Invalid list pointers,
assertion continuations, concurrent ISR mutation, full initialized task
population, and live scheduler timing remain outside this evidence. This closes
the source/list-insertion boundary; the previously completed notifier→resume→
tick-replay evidence covers ownership after a real notification, but is not
merged here into an invented blocking round trip.
