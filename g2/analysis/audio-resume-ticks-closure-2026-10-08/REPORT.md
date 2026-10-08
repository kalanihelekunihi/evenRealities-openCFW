# Pending-ready transfer before accumulated tick replay

**432 PASS original/independent resume comparisons**, extending the previously sealed pendingTicks=0 subset. [Source](../../components/audio/resume_ticks_offline/resume.c), [results](results.json), [build/dependency hashes](reproduction-receipt.json), [instructions](original-disassembly.txt).

When nested suspension count decreases but remains nonzero, pending-ready tasks and ticks remain deferred. At final resume, original0x454DCC first moves pending-ready tasks from event list0x20073D24, removes their delayed state item, and inserts them into ready lists. Only **after that transfer** does it replay0x20074A40 pending ticks through0x45504C; it clears pending ticks when replay completes. Any tick requesting a switch sets yield-pending, and the selected final yield stops before port first instruction.

A notification task already pending-ready is therefore removed from its timeout list before delayed tick replay. It is not expired a second time by that replay. The tests preserve its notification value0x800000/received marker2, while a separate timeout task keeps waiting marker1 as its deadline expires. Neither provider consumes notification state.

Fixtures vary1/2/3 pending ticks, suspension1/2, pending task absent/present, pending/timeout priorities0/1/2, tick100/0xFFFFFFFE and initial yield. Real critical/next-unblock peers execute; independent resume links the newly reconstructed independent tick provider, with hashes pinned. Wrap and timeout list transitions, replay entry ticks, complete selected state and final boundary/return agree. No child-result stubs, exception return, real scheduler timing, full initialized task population or hardware behavior. The caller's positive-suspension/list invariants are preconditions.

0x5FA0A4 is the real BASEPRI-setting helper used in critical entry; it is not itself an assertion. Actual assertion continuations remain excluded/rejected. This distinction was checked against its instructions.
