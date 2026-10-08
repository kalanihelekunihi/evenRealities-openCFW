# Case deferred ISR events: queue copy boundary and ownership

**1,936 fresh PASS cases**, separate from the preceding336 modeled-wrapper and4830 parser cases. Actual original/native copy, queue and deferred-producer paths execute with **no child result substitution**. The stock ISR wrapper now runs through its real0800c568→0800ce0c→0800c7a8→0800ad48→080001b4 call chain in680 comparisons; independent wrapper runs reconstructed producers/queue/copy with actual critical providers. No daemon/TCB scheduling execution is claimed.

[deferred.c](../../components/case/deferred_event_offline/deferred.c) and [deferred.h](../../components/case/deferred_event_offline/deferred.h) provide usable offline interfaces. Queue ABI is a recovered **prefix**, not a complete producer configuration: head+0,write+4,tail+8,read+12,send-wait list+16,receive-wait list+36,messages+56,length+60,item-size+64,RxLock+68,TxLock+69. Lists are20 bytes in fixture. Message is16 bytes: signed command-2 at0,callback ARM Thumb pointer at4,event handle at8,flags at12. xEventGroupSetBitsFromISR passes callback0800bf8d.

## New validation

| Suite | Cases | Actual execution and limit |
| --- | --- | --- |
| Copy-to leaf |240|Original0800ad48, independent and selected public body; allocated nonoverlapping item buffers, back/front/overwrite; no mutex body. Direct helper fixtures do not prove API reachability for each count/position.|
| Copy-from leaf |56|Original0800ad24, independent and selected public body; cursor advance/wrap, exact bytes to caller buffer; no removal/count/scheduler semantics implied.|
| Queue send FromISR |680|Original0800c7a8 and independent; normal back-send, room/full, unlocked and locked queues; receive-wait lists empty.|
| Deferred producer |272|Original0800ce0c, independent and selected public timer body; public producer uses actual original queue peer. Stack overwritten after return; queue bytes retained.|
| ISR wrapper integration |680|Original0800a888 through actual queue/copy; independent through native reconstruction. Valid24-bit flags, invalid flag, IPSR15/16, queue room/full. No stubs.|
| Waiter boundaries |8|Four unlocked cases stop before first instruction0800cba0(task removal); four locked cases return without touching wait list. No invented task-removal result.|

Integration item size16; lengths1/2/4 exhaust selected occupancy/write-index fixtures, length10 uses occupancy0/9/10 and index0/9. Original initialization0800ac84 statically passes length10,item size16,storage20001508,control200014b8 to0800c5d0, and stores returned handle through20000164. This grounds the stock-sized fixture without claiming actual initialization executed.

Every observed queue/control/buffer write during ISR enqueue is asserted PRIMASK1; original save080000f4 and restore080000fc execute. Input mask0/1 is restored on every completed path, and remains1 at task-removal boundary. Direct copy helpers do not acquire the mask themselves; caller critical-section responsibility remains explicit. Locked TxLock values0/1/5/126 increment; unlocked-1 leaves event-list handling enabled. No lock-overflow/hardware reachability claim follows.

## Concrete lifetime table

| Stage | Proven ownership/behavior | Boundary |
| --- | --- | --- |
| Producer |16-byte local stack message; no heap allocation in selected path.|Synthetic coherent configured queue, not runtime initialization.|
| Successful enqueue |Queue copies all16 bytes into its circular storage, updates cursor/count before producer returns.|Stack poisoning preserves queued bytes in all producer fixtures.|
| Full queue |Returns0 without message copy; ISR wrapper returnsFFFFFFFD(-3).|No automatic retry proven.|
| Locked queue |Copies message, increments lock count; no immediate wait-list removal.|Unlock/task wake path not recovered here.|
| Dequeue copy leaf |Advances/wraps read cursor, copies item into caller's buffer.|Full queue-receive operation/count decrement not tested by leaf comparisons.|
| Deferred callback |Static daemon0800b0fc reads queue message, calls function pointer with arg1/arg2 when command<0. Event callback0800bf8c forwards to actual event-set0800c4de.|Consumer dispatcher is static evidence only; no task selection/timing/actual event update execution in this batch.|
| Referenced event/callback |Pointers and flags copied by value, no deep copy/refcount acquired by producer.|Event-group deletion, cancellation, shutdown/drain and callback lifetime not proven.|

An ISR set success means the message was accepted in these fixtures, **not that event bits have already changed**. The queue owns inline command bytes after acceptance; it does not acquire ownership of the referenced event object. Any owned-buffer or epoch design must therefore preserve/validate referenced objects until actual consumer completion, handle full-queue rejection, and address disconnect/deletion/drain separately. No patch is implemented or declared safe.

## Public dependency evidence

Official FreeRTOS-Kernel V10.5.1 pin def7d2df2b0506d3d249334974f51e427c17a41c queue/timers full source and MIT license retained. Selected copy-to/copy-from algorithms and deferred-message producer agree under explicit ARM32 ABI scaffolds. Export/field translations, disabled mutex branch and actual queue peer binding are in reproduction-receipt.json. No unique release/configuration/compiler attribution or global re-pin follows.

A further mismatch remains actionable: pinned public xQueueGenericSendFromISR uses prvIncrementQueueTxLock, capped via uxTaskGetNumberOfTasks; stock selected branch0800c814 simply increments the byte. We did not compile or substitute the full public queue routine as a matching comparator. This is another scoped version/configuration lead, not whole-project source exhaustion.

Reproduce build_offline.py --gcc <ArmGNU13.3> --output <scratch>, then opencfw venv Python verify.py <scratch/deferred.elf>. Locked image/range hashes, source receipts and all test inputs retained. Prior761 seals,110 audit inputs and4 checkpoints preserved; two newly completed parser/event seals also verified. No staging, commits, production firmware or device writes.

Next worthwhile bounded target: actual nonblocking queue receive/negative-command dispatcher and event-bit application, followed by caller deletion/drain paths. These remain analyzable from the locked image; missing hardware scheduling traces limit runtime claims, not further source understanding.
