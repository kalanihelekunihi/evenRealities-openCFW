# Task-context queue send in C

The selected queue/mutex provider now includes pinned FreeRTOS 10.5.1
`xQueueGenericSend` and private `prvIsQueueFull`. They reuse the admitted queue
owner, copy helper, unlock helper and native memory providers. REA's complete
instruction view confirms stock entry `0x97c50` (334 bytes).

The function validates queue/buffer, overwrite capacity and scheduler/wait state.
It sends immediately when space exists or overwrite is requested, wakes waiting
receivers or honors the copy helper's yield result, and emits the native PendSV,
SEV, DSB and ISB sequence when required. A full queue with no remaining wait
returns failure. Blocking initializes the timeout once, suspends the scheduler,
locks the queue, updates the timeout, and either blocks a sender, retries after
space appears or exits on timeout. The inner full predicate uses equality,
including the native distinction for an overfull descriptor.

Verification:

- 5,268 paired native/C task-send cases (10,536 executions) cover zero/bounded
  items, empty/full/overfull queues, back/front/overwrite modes, raw wake values,
  masks, scheduler states, null arguments, descriptor mutations, timeout expiry,
  repeated waits and spurious resume/recheck paths. Timeout storage is normalized
  by role, initialized fully by the boundary model and checked across retries.
  Actual copy, unlock and memory providers execute; scheduler, critical, timeout,
  event and disinherit boundaries are modeled. State, snapshots, ordering, return,
  SP, callee-saved registers, masks and PendSV/hint/barrier events agree.
- 9,528 ISR-send regression cases pass with the new compiled provider.
- 8,192 integrated dynamic/static mutex-creation cases now execute actual task
  send through queue creation, initialization, reset and copying. Heap, critical,
  scheduler getter and disinherit boundaries are modeled. These cases cover all
  byte type values and descriptor/critical callback mutations.
- Negative controls reject omitted timeout initialization, reinitialization on
  retry, changing the inner full predicate to greater-or-equal and omitting the
  yield when scheduler resume returns false.

The compiler now retains the private copy helper's yield return because this
new caller consumes it. That helper changes from 114 to 120 bytes; task, ISR and
mutex comparisons cover the change. All twenty other existing function bodies
remain byte-unchanged.

All 573 R1 units compile and compose without failures or duplicate strong symbols.
Application imports fall from 190 to 189, removing only `xQueueGenericSend`;
bootloader imports remain 34. `make sources-check` and `git diff --check` pass.
Five official qualifier configurations compiled; only two already-covered
BASEPRI copies matched. Recorded C task-send/full-helper sizes are 412/28 bytes;
these new bodies remain unqualified.

The unchanged canonical plan builds a stock-identical hybrid application,
SHA-256 `0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a`,
with 3,833 source-built and 642,327 unclassified binary-pull-through bytes.
Source completeness remains false.

Finite scheduler scripts do not prove physical scheduling, interrupt delivery or
concurrency. Private frames, caller-clobbered outputs/flags and every ordinary
internal access order are excluded. Assertion comparisons cover mask, fault
address, width and value; fault-path barrier order and complete processor
exception state remain unverified. No G2 gate advances. Source, REA, probe,
qualifier and build hashes are bound in `queue-send-c-dependency-review.json`.
