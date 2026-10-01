# Queued ring TX ownership and task configuration

Completed 2026-10-01. This bounded batch extends the
[ATT copy-boundary analysis](../ring-actions-att-2026-09-30/README.md).
No firmware patch, hardware access, commit, or shared campaign change was made.

The key new result is that **WSF owns and frees the message allocation after the
handler returns, including ring TX drops**. Its free operation does not follow
the payload pointer. This supports an inline-payload message design, avoiding a
second allocation and bespoke payload cleanup on every handler branch.

## Provenance and deliverables

Firmware: `g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin`, 3,523,396 bytes,
SHA-256 `36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863`.
ARM Thumb/M-class, runtime address = file offset + `0x00437FE0`; vectors follow
its 32-byte header at `0x00438000`. No compressed bytes are interpreted as code.

- [queue_lifetime.pseudocode.c](queue_lifetime.pseudocode.c): manual behavioral
  recovery with stock addresses and explicit boundaries; syntax-checkable,
  not a firmware implementation.
- [disassembly.txt](disassembly.txt): fresh Capstone decoding of 20 bodies,
  individually checked against the authenticated corpus hashes.
- [validation.json](validation.json): **25 original-instruction scenarios**,
  20 body hashes covering 1,958 bytes, task-attribute bytes/hashes and call traces.
- [verify.py](verify.py): bounded offline Unicorn tests. Original WSF allocation
  wrappers, intrusive queue operations, enqueue/dequeue, dispatcher, ring TX
  handling and CMSIS thread-creation wrapper execute together. Provider stubs
  are enumerated in the script.

The task constructors at `0x004C4DA4` and `0x004D0AF6` failed raw Ghidra export;
this batch recovers and executes their instruction paths directly. Hash coverage
is not full behavioral coverage of every branch, nor a source-completeness claim.

## Message lifetime table

| Stage / condition | Original behavior | Ownership and cleanup |
|---|---|---|
| Producer disconnected, missing handles, or write handle zero | `0x004C4B7E` returns 0 before allocation | Caller retains its data; no message exists |
| TX wait | Gate precedes `0x004D0B64`; message connection is read again afterward | Wait is not proof that this payload has been consumed; prior batch covers timeouts |
| WSF message allocation | `0x004BF99E` requests 12+8 bytes through `WsfBufAlloc` | Eight-byte private prefix; public message begins at allocation+8 |
| Allocation failure | Producer calls TX-complete notification and returns 0 | No queued allocation to release; no useful error propagated |
| Enqueue | `0x004BF9BA` → `0x004BF9DE` → `0x00538C24` | Prefix stores handler ID at +4 and intrusive next pointer at +0; ownership passes to WSF |
| Pending message | Public +4 is borrowed data pointer; +8 is u16 length | No payload copy; caller data may change before consumption |
| Accepted event `0xAC` | `0x004C4910` calls `AttcWriteCmd` | ATT copies data before return, as established in previous batch |
| Zero/mismatched connection, null handles, zero write handle | Same handler calls TX-complete notification, skips ATT | Handler does not free payload or envelope |
| Handler returns, including unknown event | Dispatcher calls `WsfMsgFree` at `0x0052BA08` | `0x004BF9B0` frees public pointer minus 8; no nested-pointer destructor |
| Connection close | Clears connection/handles, increments epoch, cancels CCCD callbacks, posts ring event 8 | Local close branch does not drain queued WSF messages; later dispatch rejects mismatched/zero connection |
| Delayed CCCD cancellation | `0x00476ACE` clears matching pointers in a separate 64-slot callback table | Does not directly remove or release WSF message allocations |
| Local ring/WSF thread termination | Terminate thread and zero thread handle; BLE first calls callback-manager deinit | Local wrappers contain no WSF queue drain; whole-system shutdown reclamation is unresolved |

`WsfMsgSend` has no queue-capacity failure return: the observed queue is an
intrusive linked list, not the ring task's three-entry CMSIS queue. It requires
an initialized valid handler/OS state. Do not invent a queue-full cleanup branch
for this API. Allocation failure and lifecycle shutdown are separate concerns.

The original dispatcher distinguishes message events from timer callbacks and
handler-only flags. Only the message branch automatically frees the record.
A timer callback record is not an owned WSF message allocation; a test confirms
that it is not passed to `WsfMsgFree` by this dispatcher path.

## Disconnect, epoch and ordering findings

A queued TX record has no connection-generation token. Only the low connection
byte is compared with the current connection. In a synthetic sequence, a queued
record survives close, then connection-open with the same numeric ID restores
handles and permits that old TX. Changing only `ring.epoch` also does not reject
it. CCCD delayed retries have epoch guards; ordinary TX does not.

These are demonstrated **local handler semantics**, not proof that this ordering
occurs on hardware. The full master preprocessing, radio event ordering and RTOS
preemption are outside the tests. The new test also closes the connection at
the TX-wait stub boundary: the producer subsequently enqueues connection zero,
then the dispatcher drops it and frees its envelope.

Two FIFO messages pointing to the same caller memory both consume its changed
contents in the synthetic test. The dispatcher frees their two envelope bases
in order. This corroborates the borrowed-pointer issue without asserting a
hardware failure or depending on any fabricated stack timing.

For CCCD cancellation, matching entries in the 64-slot delayed table are zeroed
and the rescheduling callback is invoked once; unrelated entries remain. Tests
cover uninitialized, no-match, and matching cases. The rescheduler itself is an
external stub: its event-loop execution is not a proof about global shutdown.

## Actual static task configuration

These attributes were read from firmware bytes and passed through original
constructors and `osThreadNew` down to the static kernel-create call.

| Task | Attribute address | Entry | Priority value | Stack bytes |
|---|---|---|---:|---:|
| ring | `0x0075B8A4` | `0x004C4CED` | 46 (`0x2E`) | 4,096 |
| ble_wsf | `0x0075B838` | `0x004D0A4D` | 49 (`0x31`) | 16,384 |

The CMSIS wrapper reads priority at attribute+24 unchanged; stack bytes at +20
are divided by four before the kernel call. BLE WSF has the higher configured
priority. A promptly awakened, runnable WSF task could consume TX before the
ring producer resumes; this is a plausible mitigating explanation, not a
scheduler guarantee. These tests do not execute a kernel context switch.

Existing corpus direct-call metadata identifies priority setters in
`0x004C953E` (current-thread initialization sequence) and `0x00575470` (production
command 0x52, current-thread priority 47). Neither establishes that ring/WSF
priorities remain fixed in every mode. Indirect calls, suspend/critical-section
state, interrupt masking and runtime task identity remain outside this batch.

## Defensible patch requirements, not an implementation

1. Prefer one WSF message allocation containing the fixed header and an inline
   copy of the payload. Store its internal payload pointer in the existing
   data-pointer field. Allocate/copy completely before `WsfMsgSend`.
2. After enqueue, producer and ring handler must not free that allocation.
   Existing dispatcher cleanup will release header and inline bytes together
   after accepted, rejected, or ignored events. ATT's private copy remains
   independently owned by ATT. This replaces the previous batch's possible
   two-allocation design with fewer cleanup obligations.
3. Validate total size against WSF allocator limits, integer-width behavior and
   actual ring message limits before choosing the enlarged layout. Preserve
   payload validity until ATT returns. Allocation failure must restore the
   existing TX token accounting and expose a useful failure if the API changes.
4. If stale-connection transmission must be prevented, capture a generation token
   with the connection and revalidate it at consumption. The current CCCD epoch
   is not present in TX messages. Define the synchronization/snapshot boundary
   across the wait, disconnect and reconnect; do not rely only on numeric IDs.
5. Determine how producers are quiesced and pending messages are drained before
   WSF task teardown. Inline storage prevents a *separate* nested-buffer leak;
   it cannot reclaim an envelope left forever in a queue after termination.
6. Test accepted, every drop, allocation failure, close/reopen ID reuse,
   disconnect-during-wait and lifecycle teardown. Also preserve completion-token
   behavior; buffer ownership and radio completion are different mechanisms.

No patch bytes or speculative destructor were introduced. Final teardown policy
and allocator sizing need resolution before implementation, but the normal
send/drop ownership boundary is sufficiently established to guide that work.

## Reproduction and exact limits

```sh
~/.local/share/opencfw/venv/bin/python g2/analysis/ring-tx-ownership-2026-10-01/verify.py
clang -std=c11 -Wall -Wextra -Werror -fsyntax-only g2/analysis/ring-tx-ownership-2026-10-01/queue_lifetime.pseudocode.c
```

Result: `PASS 25 cases; 20 body hashes`; pseudocode syntax check passed. Unicorn
2.1.4 requires native JIT access beyond the macOS restrictive sandbox; Capstone
5.0.7 supplies instruction decoding. Full-image and body hashes are verified
before execution. Outputs are confined to this analysis directory.

The allocator backing, critical-section primitives, scheduler wake, master
preprocessing, ATT call, mutex/timer providers, kernel-create/terminate and BLE
callback-manager deinit are explicit stubs. ATT copy semantics come from the
previous batch's original-code tests, not this batch's ATT stub. Termination
tests establish only wrapper behavior; they do not prove a whole-system leak.
No RTOS scheduling, connection-reuse occurrence, radio success, or complete
shutdown is claimed. The next bounded gap is lifecycle callers and allocator
capacity; runtime scheduling would require a faithful scheduler model or trace.
