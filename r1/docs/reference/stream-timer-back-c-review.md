# R1 append-based stream timer constructor in C

`r1_stream_timer_create_back` in
`r1/src/application/runtime/native_stream_bootstrap.c` now supplies native
application entry `0x8a368` (84 instruction bytes). REA readback was checked
against the locked application; its evidence receipt and validation details are
in [the machine-readable review](stream-timer-back-c-review.json).

The constructor uses the existing C list append provider, preserving an existing
head. It stores the full-word callback and period, sets the sentinel to
`UINT32_MAX`, clears flag bit zero, obtains the current tick, stores context and
tick, sets flag bit one, marks housekeeping byte 15, wakes the stream and returns
the timer pointer. Callback changes to shared state and flags remain observable
through ordered volatile accesses. The existing housekeeping and tick-callback
owners are reused. Allocation failure follows the existing BASEPRI/fault path.

## Verification

`build/goal-r1-stream-timer-back-c/verify.py` passes 1,872 paired native/C replays:
384 tick, 384 wake, 384 enable, 192 initialize, 192 front-constructor and 336
back-constructor cases. Actual C list initialization, prepend and append execute.
Allocator returns, external callbacks and kernel ticks are modeled. Checks cover
full-word arguments, existing list state, callback mutations, final node/list
state and guards, ordered constructor accesses, return values, return SP,
callee-saved registers and masks. List internals are checked by final state and
call graph rather than an instruction-by-instruction memory trace.

Another 108 paired cases in `registration-chain/verify.py` execute registration
through actual C timer constructors, tick and wake providers. List, heap,
string/copy, logging, kernel tick and driver boundaries are modeled there.
The inherited 32 direct period-setter checks also pass but are not added to the
1,980 combined replay count. Five compiled negative controls are rejected:
prepend in place of append, discarded context, retained disabled bit, wrong
notification byte and returning the wake result instead of the timer pointer.

The constructor frame is 24 bytes on both paths at clock/wake calls. The nested
allocator call retains a native 40-byte versus C 32-byte depth because the list
append frames differ. The registration caller retains its earlier native
48-byte versus C 40-byte frame. Private stack words, caller-clobbered registers
and APSR are excluded; full stack identity is not established. Allocation-failure
replays observe BASEPRI 64 and the zero store at `0xffffffff`, without proving
physical exception entry or exception-register identity.

## Build and remaining gates

`make sources-check` passes. All 610 manifest units compile (536 application,
74 bootloader); both relocatable compositions pass with no failures or duplicate
strong symbols. The constructor resolves one import without exposing another:
169 application imports and 34 bootloader imports remain. The manifest is
unchanged. All 609 other objects are identical to the preceding registration
build, and all seven existing bootstrap function sections and their semantic
relocations are unchanged.

The scoped qualifier compiles the unit but admits zero bytes. The canonical
source plan is unchanged. The fresh hybrid matches the locked application hash
`0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a`
with 4,271 source-built bytes, 641,889 executable pull-through bytes and 248
resource bytes. This does not establish a full source-only link, constructor
byte identity, physical scheduling or sensor delivery. Stream dispatch and the
architectural zero-divisor provider remain unresolved dependencies.

Build reports: `build/sources-goal-r1-stream-timer-back-c/report.json` and
`build/hybrid-goal-r1-stream-timer-back-c/build-report.json`. Replay, negative
control and independent object audit results are under
`build/goal-r1-stream-timer-back-c/`; durable results are retained in the JSON
review above.

The subsequent [native stream dispatcher](stream-dispatch-c-review.md) resolves
`r1_stream_timer_dispatch` with a tested C candidate. Its deferred-cleanup
continuation at `0x89ba8` remains an explicit import, so application imports stay
at 169. The architectural zero-divisor provider and physical sensor delivery
remain unfinished.
