# Current-task delayed/suspended list transition

**96 PASS original/independent comparisons** for original `0x455FA8`. [Independent C](../../components/audio/delayed_block_offline/block.c), [results](results.json), [instructions](original-disassembly.txt), [provenance](provenance.json). This advances beyond the blocking-entry boundary in the notification-wait report; it is not a complete blocked-call execution.

Current TCB comes from `0x20074A20`, tick count from `0x20074A34`. The provider removes current state item at TCB+4 from its old list through actual `0x4560E8`. If wait=`UINT32_MAX` **and** caller allows indefinite blocking, it inserts at the suspended list `0x20073D4C` relative to that list's index, preserving the item's previous value. Otherwise it sets item.value=`tick+wait` modulo32bits and inserts into current delayed list `*0x20074A24` or overflow delayed list `*0x20074A28` if the sum wrapped below tick. For current-list insertion it lowers next-unblock time `0x20074A50` when the new deadline is earlier; overflow/suspended insertion leaves it unchanged.

Indefinite permission matters: MAX_DELAY with permission0 is a finite modulo deadline and can enter the overflow list. Zero wait still moves the task into the current delayed list when this helper is invoked; callers' own zero-wait fast paths are separate. These are tick values, not verified milliseconds.

Tests vary tick0/100/0xFFFFFFF0, wait0/1/20/MAX_DELAY, permission0/1, next-unblock10/MAX_DELAY, and empty/populated lists. Actual list removal/sorted insertion peers run, shared by original and independent provider. Independent expectations check destination, state value, old/target counts and next-unblock. Complete selected task/list/global bytes and used peer arguments agree.

Fixtures are coherent constructed intrusive lists; populated-list owner is synthetic and does not represent full initialized task population. Caller protection/critical section is a precondition. No timeout expiration, tick interrupt, ready-task selection, yield, task wake or completed notification/queue return is executed in this batch. Those are available follow-on software leads, not a global source-exhaustion claim.
