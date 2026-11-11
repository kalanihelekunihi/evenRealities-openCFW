# R1 factory task lifecycle and worker in C

The factory thread creator at `0x45c54`, stop hook at `0x45c3c`, and permanent
worker at `0x9230c` now have one C implementation each in
`runtime/native_factory_task.c`. The historical symbols containing `plan`
implement actual control flow, not simulated plans.
[Machine receipt](factory-task-c-review.json).

The creator calls ThreadNew with the C factory worker, null argument and the
stock 36-byte attributes. It publishes the returned handle to the existing
factory thread owner, testing that return value for failure. The stop hook reads
that handle once, terminates a non-null thread and clears the handle after the
call regardless of status or provider changes. The eight-byte C lifecycle
prefix supplies both callbacks adjacent to the existing thread and queue
owners. Stock RW initialization executed over poisoned RAM proves native
prefix pointers `{0x45c55, 0x45c3d}` and zero initial handles, with guards intact.

The attributes at `0x992d0` specify name `factory_test`, zero attribute bits,
null control-block/stack memory pointers, zero supplied control-block size,
8,192-byte stack request, priority 39, module field 1 and reserved field zero.
There are no invented static stack or control-block reservations. The C
attribute bytes match stock under the controlled link; callback pointer
identity is checked by symbol rather than claiming native numeric addresses.

The worker waits for synchronization group 6 and creates an eight-entry queue
of four-byte pointers. It publishes that queue handle before testing failure.
Successful startup calls the routines at `0x48ba4`, `0x8a55c`, `0x89d88`,
`0x89eec`, and `0x8a1ac` in order, then signals group 6. The first routine's
historical recovered name, `r1_wear_state_buffer_fill`, is retained as an
unresolved dependency; this review does not infer its purpose from that name.
The other four calls use the existing stream initializer, accelerometer
singleton, stream registration and temperature singleton implementations.

Every iteration polls the sensor timer and forwards its full returned timeout
to ThreadFlagsWait with mask `0x00ffffff` and option zero. The native unsigned
successful-flags condition is preserved. Receive bit `0x400000` calls the
factory record dispatcher before suspend bit `0x800000` signals group 6 and
enters a permanent maximum-delay loop. Other cases, including error flags,
feed the existing hardware watchdog and continue. This differs from BC RX's
watchdog registration and notification-error logging paths.

Both creation and queue-allocation failures call the shared architectural C
fault provider. This replay stops before that provider. Its separate
[Cortex-M review](cortex-fault-c-review.md) retains fault-register, exception
stacking and physical behavior gaps.

Verification passed 860 paired cases: 552 creator, 20 stop and 288 worker.
It covers attribute bytes, cold lifecycle data, full-width handles, shared
handle mutation, queue failure, flag boundaries, combined receive/suspend
ordering, dynamic timer timeouts and interrupt masks. Native/C provider frames
match: eight bytes for creator/stop and zero for worker. Five mutants were
rejected: wrong stack size, sync group, queue size, ignoring the polled timeout,
and accepting error flags. Production replay passed again after the negatives.

The frontier now records the creator's 36 code bytes, correcting its previous
48-byte extent that included the three literal words after its return. The
20-byte stop hook receives an evidence-backed manual entry. The worker retains
its 128-byte code extent. No candidate qualifies for executable source-plan
admission.

All 605 manifest units compile and both relocatable compositions pass without
failures or duplicate strong symbols. All preceding 604 objects are identical.
Two deeper imports become explicit: the initialization routine above and
`r1_factory_input_record_plan_dispatch`. Application imports are therefore 161;
bootloader imports remain 34. The canonical source plan is unchanged. The fresh
hybrid matches the locked application using 4,271 source-built bytes, 641,889
executable pull-through bytes and 248 resource bytes.

RTOS APIs, initialization callees, timer poll, record dispatcher and watchdog
are modeled in these replays. Permanent loops are compared through three feed
or delay checkpoints. Actual scheduling, allocator behavior, hardware startup,
factory command delivery, source-only completion and candidate byte identity
remain unproven.

The subsequent [factory boot gate](factory-boot-c-review.md) supplies the first
initialization routine and corrects its candidate name to
`r1_factory_boot_mode_schedule`. Two configuration getters and factory-mode
start are now explicit deeper dependencies.

The subsequent [factory record dispatcher](factory-record-dispatch-c-review.md)
supplies the worker's queue drain and exposes the separate factory command
router at stock address `0x625c0` as the next source dependency.
