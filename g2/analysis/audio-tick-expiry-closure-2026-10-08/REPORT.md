# Tick expiry and notification-state separation

**576 PASS full selected original tick-provider/independent C comparisons**, no child-result stubs. [Source](../../components/audio/tick_expiry_offline/tick.c), [results](results.json), [instructions](original-disassembly.txt), [provenance](provenance.json).

`0x45504C` increments tick `0x20074A34` only when scheduler-suspension count0x20074A58 is zero. If suspended, it instead increments pending ticks0x20074A40 and returns0. On unsigned tick wrap, the old delayed list must be empty; original invariant failure enters its assertion continuation. With that invariant satisfied, it swaps `*0x20074A24`/`*0x20074A28`, increments overflow count0x20074A48, and resets next-unblock0x20074A50.

For due deadlines, it removes each state item from delayed list and removes its event item if attached, raises highest-ready priority as necessary, and inserts state into its priority ready list at0x2006A49C+20*priority. It requests a switch for a task strictly higher than current priority; equal-priority readiness can request time slicing when current ready list has at least two tasks. Existing yield-pending also makes return1. This provider reports need-to-switch; it does not perform PendSV.

**It does not mark notifications received or clear their values.** Fixture notification value0x800000 and waiting marker1 remain unchanged as timeout moves the task. A ready task is therefore not necessarily a successfully notified task; the blocked API's resumed-return logic remains separate.

Cases vary tick100/0xFFFFFFFE/0xFFFFFFFF, suspension0/1/2, pending-yield, same-priority peer, event attachment and eight empty/future/due/multiple-priority profiles. Current/overflow deadline partition is constructed coherently, with valid wrap invariant and linked TCB ownership. Independent C implements inline unlink/ready insertion, rather than calling original list helpers. Complete selected TCB/list/global bytes and independent deadline/count/state expectations agree. No real IRQ cadence, exception return, blocked-call completion or live scheduling is simulated.
