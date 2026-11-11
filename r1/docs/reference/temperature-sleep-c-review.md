# R1 temperature sleep-status controller in C

`native_temperature_sleep.c` reconstructs the status controller at `0x4bad0`
(176 bytes) and its word-backed reporter at `0x4bd54` (10 bytes). It reuses the
existing capture, timing and handle owners. `native_temperature_state.h` shares
the previously tested eight-byte mode-control layout with the mode unit;
extracting the declaration leaves that unit's machine object unchanged.
[The review receipt](temperature-sleep-c-review.json) records production hashes,
REA bytes, test artifacts and the remaining proof boundaries.

The controller captures the input byte before any logging. Status exactly 1
clears the 106-byte capture, marks it active and then captures the current mode.
A saved mode of 1 returns immediately. Otherwise, a missing timing handle causes
14 timing bytes to be cleared, byte 12 to be marked and `temp` / `timing` to be
registered with order and flags 1. The returned handle is stored after the call.
Mode 1 is requested afterward, even if registration returned zero or a timing
handle already existed.

For other status values, active must equal 1. A saved mode of 1 again returns;
otherwise the saved mode is restored before the timing handle is read afresh.
A nonzero fresh handle is unregistered, then cleared after the call. Stock does
not clear the capture-active flag on this exit path; the C body preserves it.
Aliased inputs remain captured before clearing or provider mutations. No new
null check, inferred state reset or retry is introduced.

The ordinary C reporter exposes its incoming word's low byte to the controller.
Its stack frame adds eight bytes relative to stock, and it does not preserve
stock's incidental R3 residue on return. These are explicit differences, not an
instruction-identity claim. REA reports one analyzed caller; the local instruction
census identifies three direct callsites (`0x4a4fa`, `0x4a63a`, `0x4aa7a`), each
followed by the native wake routine. Unresolved indirect users remain unknown.

The production bodies pass 10,512 paired native/C direct cases covering full-
width reporter inputs, exact status/active/saved-mode gates, existing/missing
handles, all logging bits, changed log sequences, logical null faults, aliased
state inputs, interrupt masks, registration failure/success and provider
mutations. Calls, arguments, boundary/final state, preserved registers, SP and
masks agree. Six compiled defects are rejected: rereading status after logs,
short capture clearing, wrong mode restoration, a stale pre-restoration handle,
clearing active on exit and omitting post-unregister handle clearing.

Another 1,536 pairs execute the actual C mode setter/transition, memory clear,
`memset` and name registration with the new controller/reporter. They include
missing objects, registration failure, valid/corrupt modes, existing/absent
timers and saved-mode combinations. Lower object registration, unregistration,
timer operations and logs remain modeled boundaries. The direct controller's
provider-call depths match stock (24 bytes, or a released frame at its final
mode tail); the reporter retains the eight-byte increase. Raw void returns,
caller-clobbered registers, APSR and private stack bytes are excluded. Memory
observers are disabled; comparisons use boundary snapshots and final state.

All 623 units compile and both relocatable payloads compose without duplicate
strong symbols. All 622 prior objects are unchanged; imports stay at 164
application and 34 bootloader. Exact qualification rejects both new bodies.
The canonical source plan is unchanged, and a fresh hybrid retains 4,295
source-built bytes and locked application SHA-256
`0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a`.
Physical sensing, concurrent callbacks, full source linking and complete byte
identity remain open.
