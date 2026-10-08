# ISR queues, notifications and deferred event flags

Immutable candidate `ca59e91628c10bed63b695252e05b41b60b1e59fc0e551627ac4615e39e02043`; locked bootloader `f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5`, load410000. All seven cases PASS;624 inputs/157 objects unchanged. Prior681c13c6 preserved. [Exact-image validation](../same-image-validation-ca59e9.json).

[Reconstructed C](../../../../components/bootloader/thread_creation/isr_delivery.c), [interfaces](../../../../components/bootloader/thread_creation/isr_delivery.h). Eight bodies1088 original instruction bytes: ISR put41a024..41a114(240), get41a3b0..41a470(192), task count41836c..418372(6), notify418fe8..419184(412), pend callback4196e6..419708(34), deferred flags419bae..419bb6(8), ISR flags419bd2..419be2(16), queue reset419be8..419c9c(180). MIT notices intact; no upstream source copied.

## ISR queue behavior

Put/get preserve interrupt mask via native41b2f8/41b30e. Put rejects full unless overwrite mode2 with capacity1; get returns0 for empty. Put copies item_size bytes from caller immediately; get copies from ring immediately. Public message priority is ignored and get leaves output priority untouched. Null queue or null message with nonzero item size asserts in private kernel APIs; public wrappers return-4. ISR nonzero timeout returns-4, full/empty returns-3, success0.

Queue+44h is receive lock counter; +45h transmit lock counter. -1 wakes the corresponding event waiter through native event-remove/list logic. A higher-priority wake sets caller flag to1 if nonnull, without clearing it otherwise. Locked queues retain a bounded signed counter instead; the original compares its sign-extended value as unsigned against task count20027144. Counter127 asserts only when task count exceeds127. Native queue unlock later performs deferred wakes; scheduler resume transfers pending-ready items to ready lists. Queue API wrappers store PendSVSET when the local wake flag is set; no task context is restored by that store itself.

## Notification update versus readiness

ISR notify supports only index0. TCB+68h is notification value; +6ch state0(default),1(waiting),2(received). Previous value is copied before changing state to2. Low8bits(action):0 no value change;1 OR;2 increment;3 overwrite;4 overwrite only when previous state was not2, else return0. Unknown action asserts only if global tick20027148 is nonzero; with tick0 it leaves value unchanged and returns1. This recovered behavior is not an API safety recommendation.

A waiting notification target must have no existing event-list membership. Unsuspended scheduler removes its blocked state item and places it on its ready list immediately. Suspended scheduler appends its event item to pending-ready, retaining blocked state membership until native scheduler resume. Higher target priority sets caller wake flag and global yield20027158. No notification payload queue is involved: value/state change immediately, readiness may be deferred.

## Flags transport, delivery and discard

Flags ISR wrapper419bd2 calls pend4196e6 with deferred callback419bae. The actual timer queue is selected through20027180; existing native timer initialization supplies static queue20026da0/capacity50/item_size16 with storage20025cd0. The tested fixture uses a smaller coherent queue. The copied record is four little-endian ARM32 words:

```c
struct deferred_flags_record {
    int32_t command;          // -2 (0xfffffffe)
    uintptr_t callback;      // original419baf; source relocation
    uintptr_t event_object;  // borrowed pointer
    uint32_t requested_flags;
};
```

Native timer drain419546 treats negative commands as callback(arg,value), calling the real flags-set419b06 via the small void callback419bae. No returning callback stub is used. Flags are unchanged after enqueue; only consumption updates them and unblocks satisfied any/all waiters, applying clear-on-exit masks. Public41652e returns current_flags|requested_flags after successful enqueue; this is a predicted value, not callback completion or the final value after waiter clearing. A full timer queue rejects the enqueue.

| Stage | Ownership/lifetime evidence |
| --- | --- |
| Caller/pend adapter |16-byte stack record; copied synchronously before return|
| Queued | Ring owns copied scalar record; event pointer borrowed, no retain/allocation/epoch check|
| Delivery | Native queue get decrements count then timer dispatcher invokes callback; event must still exist|
| Queue reset is_new0 | Resets count/cursors/locks, may wake one sender; retains receiver wait list and ring bytes; pending callback does not execute|
| Queue reset is_new1 | Initializes both waiter lists; intended fresh-object mode, no cleanup of existing waiter nodes|
| Event deletion / whole-system drain | Not proved by these functions or fixtures; no safe deletion/cancellation guarantee|

Native reset discards an already queued flags record without applying flags, invoking a callback or freeing the borrowed object. It does not clear ring storage. A caller can therefore lose deferred work if the queue is reset; that is a concrete discard behavior, not evidence that stock lifecycle actually resets this queue in that situation.

## Validation and limits

[1480 original/source comparisons](../isr-delivery-ca59e9.json):1032/1088 mapped bytes visited. Full/empty, sizes0/1/4/8, overwrite, masks/counter-cap/saturation, optional wake output, lower/higher priority, immediate/pending-ready wake, native unlock/resume, notification state/action/fatal paths, defer acceptance/delivery and reset/discard compare queue/TCB/list/flags/output bytes. Missing body bytes include fatal spin tails and selected assertion paths; no entire-body coverage claim.

[62 public-interface comparisons](../isr-public-interfaces-ca59e9.json) execute native queue/flags wrappers and actual ISR kernel operations; no kernel result stubs. Public return codes, nonzero ISR timeout rejection, reserved flags, PendSV effects and predicted deferred flags value compare. Callback pointer normalization is limited to recognized16-byte records; the actual source target is independently resolvable from the frozen ELF symbol.

Source execution is limited to ELF executable segments; source machine never loads stock executable bytes. Coherent masks, ticks, TCBs and lists are synthetic. Calls execute in thread-mode fixtures rather than actual asynchronous IRQ exception delivery. Native pending-ready transfer and flags wake logic execute, but no task instructions/context restoration, IRQ priority/timing, post-wake loop, event deletion, global cancellation or DMA/drain guarantee.

Four former OTA numeric boundaries are native: ISR put/get, notify and flags. Candidate ledger31 aliases/23 addresses =24 aliases at16 OTA addresses +4 synthetic cuts +3 resident-ROM dependencies. Implicit pend/deferred/reset/task-count bodies close additional actual source dependencies beyond that alias count.

Next recoverable boundaries are remaining EasyLogger setter/assertion/output functions and startup/runtime alternatives. Full vectors/data/layout/compiler reproduction and byte equality remain open; no owned-buffer or event-lifetime patch implemented.

Concrete flags example: current10h/request3 returns predicted13h after enqueue; native callback produces13h with no clear-on-exit waiter, but10h with a satisfied clear-on-exit mask3 waiter. Wait result TCB+18h is82000013h before its existing accessor consumes it. Native queue reset before delivery retains10h and suppresses the callback.

Normal integrated trace does not visit ISR put/get/notify/flags. It does visit original queue reset419be8 through construction; existing native source fresh-queue initialization already performs that fresh-mode behavior inline. This batch adds a separately callable full reset body including existing-queue discard/wake behavior, directly compared.1088 is mapped function-body size, not1088 newly executed integration bytes or unique previously unimplemented bytes.

[Additional exported pend-callback/FIFO comparison](../isr-deferred-fifo-ca59e9.json) invokes the actual compiled pend body, fills the queue with3 records, rejects a fourth, then runs native timer drain and observes callbacks in FIFO order. Both event objects remain unchanged before consumer invocation; rejected record never executes. Consumer invocation is synthetic, and neither event pointer is retained/released by the queue.
