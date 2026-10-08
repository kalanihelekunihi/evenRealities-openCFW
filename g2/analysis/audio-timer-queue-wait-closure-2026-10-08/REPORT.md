# Restricted timer queue wait and list ownership

**96 PASS original/independent restricted-wait comparisons**. [Source](../../components/audio/timer_queue_wait_offline/wait.c), [results](results.json), [dependency hashes](reproduction-receipt.json), [instructions](original-disassembly.txt).

Original0x442030 sets unlocked queue RX/TX lock bytes0x44/0x45 from-1 to0 under critical protection. If message count+0x38 is zero,0x455320 appends current TCB event item+24 to receiver list at queue+0x24, then removes its ready state item and blocks it through0x455FA8. Indefinite flag overrides provided wait toMAX_DELAY; otherwise deadline is tick+wait, with current/overflow delayed-list selection. The original queue-unlock peer then restores lock bytes-1. If a message is already queued, the task remains ready and no event wait is attached.

Tests use real static queue initialization/copy, daemon-priority54 current task, audio-priority47 ready task, suspension1, finite/indefinite state, zero/small/MAX waits, wrap, optional same-priority peer and optional existing receiver. Inconsistent queued-message plus stable existing receiver cases are excluded. Independent C implements event append and links the sealed independent delayed-block provider; original critical and queue-unlock peers run. Queue/list/TCB/global bytes and independent ownership/count/deadline expectations agree.

This provider changes list ownership but does **not** itself complete a context switch. Process-or-block's subsequent resume/yield is separate. No actual daemon continuation, exception return, IRQ/tick cadence, producer concurrency or nonzero concurrent RX/TX lock accumulation is simulated. Source for unlock/deferred wake exists, but live ordering requires the relevant scheduler state.
