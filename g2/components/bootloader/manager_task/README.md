# Boot manager policy and loop

Independent C reconstruction of locked bootloader `42e224` (OTA decision),
`42e2f8` (manager task), `42e276` (setup no-op), and `42e39a` (no-op flag handler). Reference artifact:
`g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin`, base `410000`, SHA-256
`f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5`.

The manager's task entry is published by the recovered main callback; this
component separately tests its body and does not claim automatic task entry.

## Behavior and interfaces

1. Invoke setup `42e254`, no-op `42e276`, setup `42e278`, and signal helper
   `42e2ea` in that order. Setup/signaling remain provider dependencies.
2. Read the MRAM word at `007fe000`, log it, and compare exactly with
   `55555555`. This word lies outside the locked artifact. Its value on a
   real device is not established by these tests.
3. Send a 40-byte message to `42dca2`: word 0 is `1` when the flag matches,
   otherwise `0`; all nine remaining words are zero. The previously recovered
   DFU task uses these commands for update and application handoff processing.
   The manager ignores the sender's return value. Selection is not proof that
   the queue accepted it or that an application successfully booted.
4. Forever call `4162c4(mask=00ffffff, options=0, timeout=60000)` and then
   `4160e8` (tick accessor). A nonzero return below `80000000` goes to the
   no-op handler and immediately repeats the wait. Other returns test the
   unsigned tick delta against `60000`, updating only a local baseline.
   There is no periodic external action in this body. Tick frequency and
   physical elapsed time remain unknown here.

`manager_task.c` is readable source, not a ROM/opcode array. The
side-effect-free `42e276` body is reconstructed and its call order observed. A volatile local preserves the otherwise
unobservable tick-baseline update. The no-op handler keeps an assembly input
operand so its raw flag argument remains observable at the ABI boundary;
without it Clang removed the unused argument move, a mismatch detected by the
first differential run and corrected before the passing receipt.

## Validation

Run `make -C g2/components/bootloader/manager_task verify` with Unicorn JIT
permission. The current comparison at
`g2/build/bootloader-completion/manager-task/comparison.json` passes **10 cases,
214 distinct original instruction bytes**: direct flag decision and bounded
manager runs for flags `0`, `55555555`, `ffffffff`, `55555554`, `aaaaaaaa`.
Six loop inputs include zero, valid flags, high-bit errors, and tick wrap.
Logs, setup order, all 40 message bytes, wait arguments, tick calls, and raw
no-op handler arguments match original execution. This component compiles as
M4 compatibility by default; `CPU=cortex-m55` also compiles the candidate.

Synthetic boundaries: MRAM contents; setup/signaling; logger; queue sender;
flag wait and tick accessor; original memset. Source zeroing and the original
policy/branch/loop instructions execute. The seventh fixture wait bounds the
otherwise infinite loop. Hardware exception entry, scheduling, queue ownership,
MRAM programming, and downstream application execution are not validated.
No source completeness, hardware boot, or byte identity is claimed.

## Linked publisher and manager setup

`make sender-integrated` links the existing DFU publisher C. Eight cases /
328 original bytes compare manager-to-publisher call flow, all message bytes,
absent/present queue and successful/failed insertion. Successful insertion
sends bit 22 (`00400000`) to the DFU thread. Missing queue or failed insertion
logs an error, and the manager still enters its wait loop. Queue insertion and
thread flags are synthetic, not a concurrency/queue-ownership test.

`manager_setup.c` additionally reconstructs 42e254, 42e278, 42e284, 42e2a2
and 42e2ea. `make setup-compatible` passes **32 cases / 600 original bytes**.
It executes the actual reconstructed current getter, priority wrapper/kernel
setter, critical helpers, list mutation and PendSV register request.

The callback at slot `200004cc` is `42ddaf`, proved by decoding the 625-byte
authenticated initializer at 4341c0 (expanded 1371 bytes). It names the already
reconstructed DFU thread initializer. The manager creates event group slot
`20000510`, calls event runtime setup 42e53c, lowers its priority to 8, invokes
that callback, then raises priority to 48. The priority changes can request
PendSV, but these tests do not deliver a context switch. Whether the DFU thread
actually initializes its queue during this ordering requires scheduler traces
or faithful exception/scheduler execution, not an assumed timing guarantee.

42e2ea resolves the same literal (`200004cc`) then reads its+8 word, which is
DFU handle slot `200004d4`. It signals bit 23 (`00800000`) to DFU and waits for
event mask `2` (bit 1) with options 1 and timeout 20000 raw ticks. The helper considers the
wait successful whenever `(result & mask) == mask`; it does not first reject
high-bit errors. Raw ARM register shifts use low8 bits and produce zero for
shift 32..255. These edge behaviors and error-log low-byte task numbers are
covered, along with event-allocation invalid-store failure. The first fixture
exposed an incorrect literal interpretation as manager handle; it was fixed
to the DFU handle before the passing receipt.

Remaining setup boundaries: event creation/wait, event runtime 42e53c, actual
DFU thread allocation at callback 42ddae, thread flags and logger. The callback
fixture supplies its decoded pointer; context handles are synthetic. Existing
full startup stops before exception return/task execution. No hardware timing,
boot success, source completeness or byte identity is claimed.

Event-runtime initialization42e53c is now reconstructed separately in event_runtime.c: 15x8-byte queue, one-shot timer, mutex, priority38 thread with3072-byte static stack. Allocation failures log and continue; replacing an old thread ignores termination failure. Event-loop bodies42e644/42e686/42e6f4 are in event_dispatch.c. Messages store argument then callback (two32-bit words). Expired timer callbacks are removed before enqueue; queue failure or absent thread drops them. Mutex failure logs but still processes/releases. Empty table selectsFFFFFFFF and starts the timer because the stock guard excludes7FFFFFFF and zero. Counts remain raw ticks. Current fixtures prove32 initializer cases/262 bytes and445 dispatch cases/588 bytes with synthetic queue/mutex/timer/logger/callback providers; no real scheduling or timer delivery is established.
