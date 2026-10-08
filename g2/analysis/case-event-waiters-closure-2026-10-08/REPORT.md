# Case event waiters, object ownership and kernel revision discrimination

**384 fresh PASS original/independent comparisons**, with actual original task-unblock0800c1cc, list-remove0800bf2c, ready-list insert0800bfe2 and scheduler suspend/resume peers executing. **No child entry result stubs.** [waiters.c](../../components/case/event_waiters_offline/waiters.c) reconstructs selected valid-argument event-set0800c4de; it is not a full event-group API/kernel. Earlier inventory/queue/consumer counts are not rerun/new coverage here.

## Recovered waiter interface

Event bits+0; list control at+4, sentinel at+12. Waiter list item is20 bytes: value+0,next+4,previous+8,owner TCB+12,container+16. TCB state item+4,event item+24,priority+44. Requested mask is low24 bits; value control flags clear-on-exit01000000,wait-all04000000. Match is any overlap for wait-any, complete inclusion for wait-all. The event-set body first ORs set bits into existing bits, evaluates waiters, accumulates masks requested for clear-on-exit, then clears the accumulated bits after traversal.

A matching waiter is passed event snapshot|02000000 to actual task-unblock. That provider requires scheduler suspended, stores snapshot|82000000 in event-item value, removes event item from event-group list and state item from delayed list, then links state item into ready list. Event item container becomes NULL; ready state item container becomes20000ff4 for tested priority0. **No task allocation/free or deep object ownership is acquired by this move.** The TCB and its embedded items must remain valid while linked.

Verifier asserts scheduler-suspended count>0 at each unblock, event-item unlink/ready-list ownership after each match, returned bits, callback arguments, all affected event/TCB/list/global bytes and restored critical depth/mask. Requested masks8/40/48, existing/set bits0/8/40/48, any/all, clear/no-clear and nesting0/1 yield384 cases. Equal-priority current/blocked TCBs, one coherent delayed waiter, empty pending-ready list and no pending ticks/yield are synthetic fixtures; unexpected yield fails the test. **No actual task schedule, higher-priority switch, timer expiry, multiwaiter race or hardware trace is observed.** General arbitrary initial PRIMASK restoration is not implied by nesting critical providers.

Clear-on-exit changes the stored event field after the satisfied waiter receives the pre-clear snapshot. An app cannot read final flags and assume they equal what the woken task received. Repeated notifications may coalesce; lifetime protection must cover both queued borrowed event handles and linked waiter TCB/list items.

## Deletion/drain boundary: no fabricated stock binding

Stock creation wrapper0800a836 supports dynamic/static storage; dynamic constructor0800c48c requests32 bytes, initializes bits/list and allocation marker. This is static evidence only in this batch. The registered435-function corpus direct-BL screen is preserved in lifecycle-static-xrefs.json. Direct free calls belong to known timer/thread allocation failure, deleted-task cleanup or positive timer deletion paths; **a stock event-group-delete function and a caller that closes/drains the case deferred queue before event deletion have not been bound**. Indirect calls/unregistered regions are outside that screen. Do not interpret this as proof deletion cannot occur or that pending pointers are safe forever.

Official pinned public vEventGroupDelete unblocks event-list waiters and frees dynamic event storage after scheduler resume; its body does not cancel pending deferred ISR callbacks or reference-count the borrowed event handle. That is **public source behavior**, not execution or attribution of an unidentified stock delete body. Combining a borrowed queued pointer with freeing an object illustrates a conditional lifetime requirement, not a hardware race finding. A safe ownership design needs an actual bound close/delete call path or external runtime evidence showing producers quiesce and callbacks drain before object release. Do not implement speculative memory management from this batch.

## Kernel revision lead narrowed

Official FreeRTOS-KernelV10.4.3 resolved to immutable commit **9c048e0c71ee43630394981a86f5265bc57131e4**. Its xQueueGenericSendFromISR directly increments cTxLock, agreeing with the stock branch0800c814..c81a already executed in the preceding queue suite. RegisteredV10.5.1 uses prvIncrementQueueTxLock, capped via uxTaskGetNumberOfTasks. Full sources and immutable receipts retained. This is fresh **static source discrimination**, not a newly compiled full-public-queue comparator, unique whole-kernel release attribution, or permission to re-pin dependencies. Other bodies/configuration/compiler need separate comparison.

## Reproduce, limits and next work

Build with build_offline.py --gcc <ArmGNU13.3> --output <scratch>; run opencfw venv Python verify.py <scratch/waiters.elf>. Image/tool/source/output hashes and original disassembly retained. All816 prior sealed entries,110 audit inputs and4 checkpoints verified unchanged. No staging, commits, production firmware/device writes.

Next actionable source work: compare full older public queue body against stock with explicit ABI/config scaffold; follow actual event-object creator/global users and queue unlock/deleted-task paths, or extend coherent multiwaiter/higher-priority fixtures while retaining the scheduling limit. Exact lifetime blocker is **unbound stock close/delete/drain path plus missing runtime producer/consumer ordering**, not absent decompilation tools. No global source-exhaustion or patch-safe claim.
