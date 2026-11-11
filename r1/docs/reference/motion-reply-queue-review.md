# R1 sensor reply through the actual C BLE queue dispatcher

This review closes the modeled-sender boundary in the
[legacy reply sender review](legacy-reply-c-review.md). The fixtures link and
execute the production C connection getter, legacy sender, type-2 BLE queue
dispatcher and `memcpy`. A second fixture also links and executes the C motion
adapter, its factory-state owner, memory-clear bridge and `memset`. C runs
reject execution entering the stock application image. REA byte reads and
local disassembly bind the stock reply, getter, queue veneer and shared body
to the locked application. [Machine-readable evidence](motion-reply-queue-review.json)
records these receipts, replay results and source/object/fixture hashes.

There are 2,100 paired stock/C reply-chain cases and 348 paired motion-chain
cases. They cover invalid connection handles, null payloads, absent queues,
allocation failures, successful and failed submissions, zero and unaligned
payloads, lengths through 255, queue-occupancy multiplication wraparound,
interrupt masks, and external or caller-stack input buffers. The motion
fixture supplies an inactive factory mode and valid sample count; active-mode
caching and empty-sample behavior remain covered by the earlier motion review.

The actual dispatcher copies the header and payload into a heap envelope
before calling the queue. Queue submission receives a pointer to that envelope
pointer, priority zero and timeout 100. Header fields retain the handle, type 2
and full length. After submission, the fixture overwrites the original payload,
including the actual motion adapter's stack packet; the envelope payload stays
intact. Success transfers ownership and signals the worker. Failure frees the
envelope and the sender returns the low-byte failure. Provider call order,
arguments, heap snapshots, final ownership/free state, preserved registers,
stack restoration and interrupt masks agree with stock.

Four separately compiled dispatcher defects are rejected: copying one byte too
few, choosing type 1, omitting failure cleanup and omitting the worker signal.
The fixtures execute the actual memory-copy implementations without memory
observer hooks; snapshots are taken at provider boundaries. This avoids the
known Unicorn Thumb-IT observer interaction and does not assert instruction-by-
instruction memory-access identity.

Allocator, RTOS queue operations, thread signaling and zero-valued log-mode
remain modeled providers. The review does not execute a physical BLE worker or
an asynchronous consumer. Caller-clobbered registers, APSR and private stack
bytes are excluded; the motion callback's void return is also excluded. Frame
depths still differ: ordinary provider calls are native 80/C 64 bytes in the
reply fixture and native 128/C 120 in the motion fixture. Logging helper paths
can add a further C frame. No exception-stack identity is claimed.

The audit revalidates all 619 production source/object hashes and both successful
relocatable compositions. Application imports remain 166, bootloader imports
34. This review changes evidence only; firmware sources and the canonical exact
source plan remain unchanged. Physical delivery, full source linking and the
remaining hardware and instruction-identity dependencies remain open.
