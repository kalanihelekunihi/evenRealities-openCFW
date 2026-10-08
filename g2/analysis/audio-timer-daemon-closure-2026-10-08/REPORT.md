# Timer daemon iteration order and actual static configuration

**40 PASS daemon-order comparisons plus1 PASS actual static-creation comparison**. A separate original-only constructor-entry probe preserves the argument boundary; it is not another complete-creation case. [Source](../../components/audio/timer_daemon_offline/daemon.c), [ordering](results.json), [creation](creation-results.json), [entry probe](creation-boundary-results.json), [instructions](original-disassembly.txt).

Actual constructor0x47E674 forms entry pointer with aligned PC: `((0x47E6B2+4)&~3)+0x1C5 = 0x47E879`. The entry is0x47E878, including its prologue. This avoids treating the unaligned instruction-PC arithmetic as a different entry.

Actual static create0x454820 receives `{entry0x47E879, name0x78EBCC, depth4096, arg0, priority54, stack0x2003FA98, TCB0x20071EA0}`. Original constructor and independent selected constructor execute real static-memory and create peers in an isolated zero-BSS/already-created-queue fixture. They return1, publish the handle/current TCB, initialize ready-list54 and priority54, and agree over the selected RAM region. Stack is **4096 words/16KiB**. Scheduler is not started. Compared with separately recovered audio task priority47, priority54 is an important preemption constraint; it is not proof of a live task population or every timer-delete caller's priority.

## Iteration order

`0x47E878` repeats:

```
expiry = next_expiry(&current_list_empty); //0x47E8F2
process_or_block(expiry, current_list_empty); //0x47E88C
process_received_commands(); //0x47E97A
```

A nonempty list with sampled now≥expiry goes through original expired-timer0x47E83A to callback adapter0x449398 **before command drain in this iteration**. Tests publish real Stop3 or Delete5 messages (or none), then invoke the actual daemon entry. At ticks150/151 with expiry150, they stop at user callback first instruction with the command still queued. Successful dynamic auxiliary release before daemon entry and two actual-allocator reuse cases reproduce the earlier synthetic read/order result through the real outer loop, rather than calling the due helper alone.

At tick149, empty command queue stops at restricted-block0x455320 entry; nonempty queue stops at port-yield0x4420BC entry. No callback return, block completion, yield or context handover is fabricated. Independent C supplies next-expiry and one-iteration ordering with shared original process/drain peers. It is not an independent full timer kernel.

**This is constructed iteration-entry state, not a proven live defect.** A daemon already blocked inside process-or-block can resume and reach command drain before starting another expiry-first iteration. Higher-priority receiver wake can preempt a sender before auxiliary free, as shown by the delete-wake successor. Need actual daemon PC/wait state, sender priority, tick/queue history and scheduler trace to establish real lifetime reachability. The test does not demonstrate that stock audio-priority47 can install the synthetic queued-delete state while daemon54 runs.
