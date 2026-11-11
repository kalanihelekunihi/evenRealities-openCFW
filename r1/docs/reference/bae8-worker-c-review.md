# R1 BC receive queue startup and worker in C

The stock function at `0x92178` (198 code bytes) now has one C candidate,
`r1_bae8_input_task_plan_startup`, in `runtime/native_bae8_worker.c`. Despite
its historical plan-oriented symbol name, it implements the permanent RX
worker, not a simulated startup plan. [Machine receipt](bae8-worker-c-review.json).

It waits for synchronization group 2, creates a 50-entry queue of four-byte
message pointers, and writes the returned handle to the existing RX queue
owner. A successful creation signals group 2, registers `ble_msgrx` with a
10,000-unit watchdog interval, and writes the watchdog handle to the existing
RX watchdog owner. There are no new shared-state owners or duplicate copies.

Each iteration arms the current watchdog, waits for `0x00ffffff` thread flags
with option zero and infinite timeout, then disarms the current watchdog.
The unsigned condition `flags - 1 < 0x7fffffff` accepts the native successful
flag range. Receive bit `0x400000` invokes the actual drain symbol; suspend bit
`0x800000` then arms the watchdog, signals suspension for group 2, and enters
an infinite maximum-delay loop. Receive runs before suspension when both bits
are set. Other successful flags proceed to feeding the current watchdog.
Invalid/error flags emit the stock notification-error diagnostics according
to the current logging modes, then feed and continue. Shared watchdog values
are reloaded after each provider; registration uses its returned handle even
if a provider has changed shared state in the meantime.

The native queue-allocation failure path sets BASEPRI to 64 and attempts a
zero word write at address `0xffffffff`, followed by an infinite loop if the
store returns. Portable C cannot implement that architectural transition.
The candidate explicitly calls the unresolved nonreturning
`r1_bae8_rx_allocation_fault` rather than silently returning or pretending a
trap is reconstructed. The comparison ends before that transition. Its
physical behavior and implementation remain open.

Verification passed 720 paired stock/C cases, ending at the allocation-fault
boundary or after three feed/delay checkpoints. Cases cover allocation success
and failure, valid and invalid flag boundaries, combined receive/suspend flags,
logging modes including changing mode responses, both interrupt-mask states,
and queue/watchdog mutations at provider boundaries. Native and C provider
frames are both zero bytes. Ordered accesses to the shared queue and watchdog
are compared. Five mutants were rejected: wrong queue capacity, accepting error
flags, wrong receive bit, skipping watchdog feed, and wrong synchronization
group. Production replay passed again after the negative controls.

All 601 manifest units compile and both relocatable compositions pass without
failures or duplicate strong symbols. All preceding 600 objects are identical.
The architectural fault adds one explicit import: 161 application imports and
34 bootloader imports remain. No bytes qualify for the canonical source plan.
The fresh hybrid matches the locked application with unchanged coverage:
4,271 source-built bytes, 641,889 executable pull-through bytes and 248 resource
bytes. This does not establish a complete source-only build or byte identity
of the candidate.

Synchronization, queue creation, watchdog, drain, delay and logging providers
are modeled in this replay. The drain itself has a separate review and retains
its documented frame gap. RX thread creation, its static attributes and stack,
the failure transition, actual RTOS scheduling and physical BLE behavior remain
separate unfinished requirements.

The subsequent [thread creator](bae8-thread-c-review.md) supplies creation,
static attributes, reservations and lifecycle prefix. It corrects the worker
signature to accept the RTOS argument without changing the compiled object.
Scheduling, the failure transition and device validation remain open.

The subsequent [Cortex-M fault adapter](cortex-fault-c-review.md) supplies the
previously unresolved C provider. Fault-register identity and physical exception
behavior remain unproven.
