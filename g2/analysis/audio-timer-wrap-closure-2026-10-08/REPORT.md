# Timer sampled-time wrap and autoreload insertion

**128 PASS original/independent sampled-time/list-switch comparisons**. [Source](../../components/audio/timer_wrap_offline/wrap.c), [results](results.json), [instructions](original-disassembly.txt), [provenance](provenance.json).

`0x47E916` obtains real tick through0x454EFE. If now<last sampled time0x20074AB8, it calls0x47EA90 to expire every timer remaining in the old current list, passing `now=UINT32_MAX` to expired-timer0x47E83A, then swaps current0x20074AA8/overflow0x20074AAC. Only after the switch helper returns does it publish switched1 and update last-time. Without wrap, switched0/last-time/return update directly.

Tests with an old current timer stop at real user callback entry **before** list swap and sampled-time/output publication. Single-shot clears active/unlinks before callback. Selected autoreload branch executes the actual reload/insertion peers first: expiry0xFFFFFFF0+period50 wraps to34, inserts into overflow list and keeps active, then enters callback. With an existing overflow deadline25, actual sorted insertion preserves the earlier head. No callback return is supplied, so further old timers and completed nonempty-list swap are not claimed.

Empty old-list cases complete actual swap/publication; no-wrap cases leave list pointers untouched. Fixtures vary old timer presence, autoreload, existing overflow timer, two wrapped/two nonwrapped ticks, real queued Delete5 with dynamic auxiliary free or no delete, and suspension0/1. Queue Delete is not drained by sampled-time handling. Suspension1 reflects the process-or-block caller's suspension condition but remains synthetic. Original and independent wrappers/loop share actual tick-get and expired/reload/adapter peers; complete selected heap/list/time/output state agrees.

This strengthens software ordering across wrap and shows where autoreload storage is reinserted. It does not prove live deletion/callback interleaving, full repeated callback/catch-up execution, task preemption or hardware lifetime failure. Those require caller/scheduler state beyond these fixtures.
