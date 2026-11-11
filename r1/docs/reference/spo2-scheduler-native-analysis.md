# R1 SpO2 scheduler native contract before C conversion

Follow-up: the [C scheduler review](spo2-scheduler-c-review.md) now implements
this contract with the 112-byte record offset preserved. Unresolved/C status
below describes this earlier native-analysis snapshot.

The [receipt](spo2-scheduler-native-analysis.json) binds REA bytes, locked
artifact/ELF hashes and **3,424 completed native probes**, including **640 with
the actual flag getter and record reader**. The distinct scheduler body
`0x4af10` through `0x4b08f` is **384 bytes** and now has an unresolved frontier
entry. This is native analysis, not a C implementation or qualified source.

Both initial flag bytes must be zero and mode exactly 1. After the health flag
and wear predicate, only timing-stream slot 1 is checked. Slot 0 and an existing
timer **do not block registration**. Nonzero input skips the clock and labels
success `hourly`; zero input uses `catchup`. The unsigned local-time calculation
`3600 - timestamp % 3600` must exceed 150 seconds. Accepted starts use 120
seconds: the later subtraction/clamp cannot shorten that value after this gate.
Boundary and wrapped timestamps are covered.

Unlike the HRV scheduler, this routine registers the **stream first**:
`spo2` / `timing`, callback `0x4ada1`, arguments 1,1, publishing the returned
handle to slot 1 after the provider. Failure logs and returns. Success then
creates a timer with callback `0x4b235`, 120,000 milliseconds and argument zero,
publishing its result late. A previous timer handle can be overwritten without
release. There is no session-buffer clear.

Failed timer creation logs, reloads stream slot 1, **unconditionally** calls
unregister—even if logging has changed the slot to zero—and clears the slot
after that provider returns. It does not call the timer-release helper. The
probes cover provider changes to stream/timer during registration, creation,
logging and unregister. Late publication and cleanup ordering are verified
against an independent control-flow/state model.

The native scheduler frame is **40 bytes**, followed by the existing eight-byte
flag-getter frame and 64-byte record-reader frame. The record therefore starts
**112 bytes below scheduler entry**. Full, prefix24, prefix25, flag-only and
absent writes, four flag-byte inputs, both storage statuses and sixteen poisoned
stack seeds are covered. Read status is ignored; absent-write flags vary across
seeds. A C caller must prove this record location and raw-byte behavior with
the actual getter/reader, rather than replacing them with a modeled boolean.

Calls, arguments, logs, public state/guards, record contents and offsets, saved
integer/FP registers, SP, masks and FPSCR are checked or recorded. NV storage,
wear/time, registration, timer creation, unregister and logging providers are
modeled. Their real physical allocation, concurrency and complete callback
behavior remain outside this proof. All 661 current source/object hashes,
manifest and canonical source plan remain unchanged; the only frontier change
is the new unresolved scheduler entry. Final source-only linking and physical
SpO2 scheduling remain unproven.
