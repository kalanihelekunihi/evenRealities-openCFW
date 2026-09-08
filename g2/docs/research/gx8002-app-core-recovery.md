# GX8002 application-event core recovery

The authenticated pinned NationalChip application-core source matches the
callback and initialization cluster following the model interface. The
[evidence record](gx8002-app-core-recovery.json) records Git blob and SHA-256
identities for the upstream C and two headers, plus candidate package offsets.

`app_core_ops` is read from `0x20026D38`. The upstream `LVP_APP` layout places
resume callback/context at offsets 24/28 and suspend callback/context at 16/20,
matching stock dispatch. Initialization supplies a 64-byte queue buffer with
8-byte events, calls the optional application initializer, registers suspend
and resume callbacks, and supplies watchdog reset/timeout arguments 3000/2999.
These observations identify a connected application-runtime recovery target;
they do not qualify every callee or configuration branch.

The new `runtime_gx8002_app_resume.c` uses the upstream layout and target ABI
assertions. `verify_gx8002_app_resume.py` authenticates both included headers,
compiles with `-fno-shrink-wrap`, and links the application-pointer symbol at
`0x20026D38`. All 28 emitted bytes match stock, with no unresolved relocations.
The [verification record](gx8002-app-resume-verification.json) pins source,
headers, flags and linker script. Nine host cases cover null application,
null callback, private-context forwarding and ignored callback return values.
The callback is now included in the experimental firmware builder.

The experimental codec now has 30 source-compiled functions and 324,742
retained bytes. This byte-exact replacement preserves the existing package hash.
Other application-core functions remain reconstruction candidates.

The next dependency is the suspend callback's watchdog-stop call at package
`0xFD38`: `movih` selects `0xA0700000`, then one 32-bit read, clearing bit zero,
one 32-bit write and return. Its 12-byte body precedes the reboot path at
`0xFD44`, which performs additional clock/reset writes and loops indefinitely.
These remain retained; a returning replacement must not stand in for reboot.

The suspend callback now also has a C reconstruction using the pinned upstream
layout. Its verifier links the watchdog-stop call to `0x102067AC` (package
`0xFD38`), and all 32 bytes match the stock callback at `0x1222C`. Nine host
cases require watchdog stop before optional callback dispatch, including null
application/callback cases. The watchdog is mocked in these host cases.
The [suspend report](gx8002-app-suspend-verification.json) remains explicitly
not source-admitted because its watchdog dependency is not yet integrated.

`runtime_gx8002_watchdog_stop.c` reconstructs the one-read/one-write bit clear.
Default CK804EF GCC emits 14 bytes using `andni`, versus the original 12 bytes
using `bclri`. This candidate must fit or be relocated and qualified before
admission. No binary fallback is represented as recovered source.

## Watchdog and suspend admission

The size gap is resolved with an explicit `bclri` inline assembly expression
using a read/write low-register constraint. GCC's pinned `csky_split_and`
selects the wider `andni` first for this mask; the source documents the reason
for selecting the original instruction. Volatile C still performs the single
32-bit read and write. This is readable instruction source, not an opaque
array or extracted instruction payload. The
[watchdog verifier](gx8002-watchdog-stop-verification.json) requires all 12
compiled bytes to equal stock and rejects unresolved dependencies.

Both watchdog stop and the 32-byte suspend callback are now integrated in the
experimental codec. Their exact bytes preserve the existing package hash.
Seven relevant tests pass; the callback tests mock watchdog stop, while the
real target routine is qualified by exact emitted-byte comparison. Device
power-state behavior and timing remain unqualified. Earlier non-admission
notes above describe the preceding reconstruction stages.

The event tick body at package `0x122D4` consumes one queued event, conditionally
calls AppEventResponse, reloads the application pointer, and conditionally calls
AppTaskLoop. It then calls `0x118C0` (candidate UART async tick from upstream
call order) and `0xFD2C` (watchdog ping), returning zero. Reloading the application
pointer after an event callback must be preserved because callbacks can change
it. Watchdog ping writes 118 to `0xA070000C`; its executable body ends at
`0xFD36`, followed by two alignment bytes. These are next recovery dependencies,
not new source admissions.

The event-tick C candidate now compiles to 80 bytes with the pinned SDK headers.
It remains relocatable and differs in branch/register choices, so it is not
source-admitted. Eight host cases cover empty/populated queues and callbacks
that retain, replace or clear the application pointer. They verify event
payload delivery and event callback → current application loop → UART service
→ watchdog service order. Queue code is real upstream C; UART/watchdog service
functions are host mocks. The candidate reloads the current application after
an event callback. The [candidate record](gx8002-app-tick-candidate.json) pins
source/object hashes and flags.

A separate watchdog-ping C candidate emits ten bytes exactly matching stock
at `0xFD2C`; two following alignment bytes are excluded. Neither candidate is
integrated yet. The UART service body remains the key dependency to reconstruct
before qualifying the complete event tick.

The UART async service is now matched to the pinned upstream receive dispatcher
and reconstructed in `runtime_gx8002_uart_async_tick.c`. Target ABI assertions
check the 32-byte packet, 28-byte registration, body pointer and length offsets.
The native compiler emits 132 bytes, but linked target equivalence is still
pending. The [candidate record](gx8002-uart-tick-candidate.json) authenticates
the upstream C/header evidence and records dependencies.

Thirty-two host cases cover empty queues, flags 0/1/2/255, CRC success/failure,
missing registrations and duplicate matches. CRC is checked only for flag 1;
the first matching command/port registration wins, and its return value is
propagated. CRC and logging are mocks in this host test, not recovered providers.
Their target bodies at package `0x12E34` and `0x101B0` remain to be qualified.
No firmware source admission occurs in this step.
