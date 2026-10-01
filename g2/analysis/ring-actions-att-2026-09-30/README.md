# Ring gestures, application dispatch, and ATT ownership

Bounded behavioral recovery, completed 2026-10-01, continuing the
[ring protocol batch](../ring-protocol-2026-09-30/README.md). This is annotated
pseudocode and an interface reference, not original source or a firmware patch.
Shared campaign state and previous batches were not modified.

The useful results are a named gesture-to-page mapping, a manually recovered
application serializer that Ghidra failed to decompile, and the precise point
where ATT stops borrowing the caller's payload. The tests execute stock Thumb
instructions: **46 scenarios, 13 authenticated bodies, 4,996 bytes**. A body hash
is provenance, not a claim that every branch in that body has been understood.

## Evidence and files

Input: `g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin`, 3,523,396 bytes,
SHA-256 `36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863`.
ARM Thumb/M-class addresses use file offset + `0x00437FE0`; the 32-byte header
precedes vectors at `0x00438000`. The verifier checks the image hash and each
body against `g2/research/corpus/apollo-main/ghidra/open-2026-09-29/functions-000.jsonl`.

- [actions_att.pseudocode.c](actions_att.pseudocode.c): readable manual recovery,
  with partial paths and external operations explicitly marked.
- [ring_actions.h](ring_actions.h): usable, allocation-free gesture mapping and
  explicit little-endian application record encoding for host/simulator tools.
- [disassembly.txt](disassembly.txt): fresh instruction bytes, addresses, and body hashes.
- [validation.json](validation.json): original-code call traces, cases, versions,
  direct-call sites, and individual body hashes.
- [verify.py](verify.py): reproducible original-instruction tests with explicit stubs.

## Received gesture to application action

The prior batch established ring type decoding into source 4. Retained strings
returned by `0x004C5892` now establish the event names; these are not guesses
based on gesture direction. Display dispatch is at `0x00442D86`.

| Ring type | Input event | Retained name | Page event / observed action |
|---|---:|---|---|
| 1 | 0 | SINGLE_CLICK | `0x0A`, source word supplied |
| 2 | 1 | DOUBLE_CLICK | `0x48`, source word supplied |
| 0 | 3 | LONG_PRESS | Context-dependent; page event 8 or system/menu handling |
| 5 | 4 | UPROLL | `0x44`; dashboard increments item index when allowed |
| 4 | 5 | DOWNROLL | `0x45`; dashboard decrements item index when allowed |
| 8 | 14 | RELEASE | `0x4A`, two signed values supplied |

This does not assign a universal app operation to every click: the active page
handles its event. For the dashboard callback `0x004E8BCC`, roll events call
`0x004E7D20` with direction +1 or -1. With a valid object, no blocking state or
animation, and an in-range index, it changes the index and requests a scroll
of +304 or -304 from the current position, then notifies `0x004E772C`.
Tests cover middle positions, both boundaries, and blocking state. The boundary
helper is stubbed; wrapping is not established. GUI animation is also stubbed.

Long press has several paths. If `0x00442D64` permits page handling, it emits
page event 8. When a transition is busy, only page ID `0x30` gets that event.
Otherwise page-kind zero closes factory page `0xE0` via `0x0046AE9C(1,0xE0)`,
or sends system command 3 for device role 1. Page-kind one has menu-stack paths
left abstract in the pseudocode. Tests cover the direct page event and normal
role-1 command-3 branch; other long-press branches are static observations.

### Input arbitration and record boundaries

`0x004C5916(source,event,a,b)` publishes sync ID `0x108`, a 12-byte local record:
u16 source at +0, u32 event at +4, bytes a/b at +8/+9. Stock does not initialize
the padding. Flash registry `0x006A4620` contains ID `0x108`, followed by the
Thumb callback pointer `0x004C5DBD` at +4.

That callback, input manager `0x004C5DBC`, drops device role 2; tracks dual-hold
and usage; arbitrates competing sources; then applies dual-hold/settings
filters. If the active source is neither `0xFFFF` nor the incoming source,
elapsed time below 1001 kernel ticks suppresses the event. Tests distinguish
1000 from 1001. This is **ticks**, with no new clock-rate claim. Accepted-source
timestamp/source updates precede the later filters; RELEASE resets the active
source to `0xFFFF`. This explains why a valid ring event need not produce a
visible action. `DECA_CLICK` (`0x1010`) routes to system command `0x109`.

Ordinary events call `0x00465748(source,event,(a<<16)|b,0)`. Its raw Ghidra export
failed with an address-range construction error. This batch manually recovers
the relevant behavior from its 962-byte body, SHA-256
`d5b9d4f08e694a1bdf791a1b898fc09bbb2997bc5b5343a27e32d81f68f8c9f9`:

1. Require the local queue global; allocate a 12-byte envelope and 12-byte body.
2. Body: `03 07 source_u16le event_u32le extra_u32le`.
3. Envelope: u32 mode +0, u16 route +4, u16 length +6, 32-bit body pointer +8.
   Role 1 uses route 3 and its output queue; role 2 uses route 0/local queue and
   signals flags 2. Other roles release both allocations.
4. Allocation failure cleans up what was allocated. Queue failure frees both,
   then enters assertion/fault handling; that fatal path was not executed.

For source 4, event 0, a=7, b=9, the body is
`03 07 04 00 00 00 00 00 09 00 07 00`. Original-code tests verify all six ring
event bodies and both allocation failures. Queue operations are stubs; success
means serialization and the selected branch were verified, not delivery by a
real initialized queue.

Display input consumes the packed ten-byte suffix: u16 source +0, u32 event +2,
u32 extra +6. Roll/release dispatch sign-extends the low and high halfwords into
two int32 values, so the example becomes `[9,7]`. Static supporting callers are
sync command-7 handling in `0x0045B14C` and the display worker `0x004437E0`,
which retrieves sync data and dispatches message type 7. Tests cover these
boundaries separately, not the entire cross-device queue/transport/GUI chain.

## ATT copy and release boundary

`AttcWriteCmd` at `0x00539DEA` allocates a private packet using
`attMsgAlloc` (`0x004B50AE`, wrapping WSF allocation), constructs ATT opcode
`0x52` and the little-endian handle, then calls memcpy at `0x00539E2C`:

```text
application payload --copy n bytes--> owned_packet + 11
                                     +0 u16 ATT length n+3
                                     +8 0x52
                                     +9 u16 handle
```

The copy has completed at `0x00539E30`. `attcSendMsg` (`0x004B5640`) receives
the new packet and op 10, not the caller pointer. For normal valid BLE lengths,
the caller buffer may be released **after AttcWriteCmd returns**. The accepted
test overwrites the caller's buffer after return and confirms the queued ATT
packet still contains the original payload. Example handle `0x10`, payload
`00 1A 8A 01 12 34` becomes ATT bytes `52 10 00 00 1A 8A 01 12 34`.

`attcSendMsg` checks connection/MTU under a lock. It releases its private packet
on absent connection/zero MTU, blocked connection, excessive ATT length, or
WSF-envelope allocation failure. Blocked and MTU rejection invoke callback
statuses `0x71` and `0x77`. On success a 12-byte WSF envelope carries the packet
pointer to ATT, transferring ownership. Tests exercise accepted, missing
connection, blocked, MTU-rejected, packet-allocation, and envelope-allocation
paths. The API's return register is not treated as a reliable success status.

Later `attcSendSimpleReq` (`0x00530E30`) clears the pending pointer at CCB+8
before handing the packet to `attL2cDataReq` (`0x004B50BA`). Separate cleanup
helper `0x00531AC0` frees the pointer at message+4 and zeros it. Both operations
are tested. The final L2CAP/radio completion and release path is **not** traced;
it is not needed to establish the original caller buffer's copy boundary.

### Consequence for a possible owned-buffer TX patch

The prior batch demonstrated a borrowed stack pointer across queued dispatch
under synthetic scheduling. A feasible design is to allocate/copy before the
application WSF enqueue, keep that application-owned copy through the queued
ring send handler's `AttcWriteCmd` call, then release it after return. Stale
epoch, disconnected, discarded-message, and enqueue-failure paths must also
release that application copy exactly once. Preserve existing WSF-envelope
ownership, and do not free ATT's private packet after a successful handoff.

This is a design boundary, not an implemented patch or a claim of a hardware
failure. Actual task priorities/preemption, every discarded-message path, and
allocation-failure reporting still need review before implementation. ATT
acceptance is not a radio acknowledgment.

## Reproduction and limits

```sh
~/.local/share/opencfw/venv/bin/python g2/analysis/ring-actions-att-2026-09-30/verify.py
clang -std=c11 -Wall -Wextra -fsyntax-only g2/analysis/ring-actions-att-2026-09-30/actions_att.pseudocode.c
clang -std=c11 -Wall -Wextra -Werror g2/analysis/ring-actions-att-2026-09-30/test_header.c -o /tmp/opencfw-ring-actions-header-test
/tmp/opencfw-ring-actions-header-test
```

All six host header records in `host-validation.txt` match the `queue_put.body`
bytes in the identically named original-instruction cases. The host test also
checks unknown ring-type rejection. Pseudocode syntax checking passed.

The verifier uses Capstone 5.0.7 and Unicorn 2.1.4. macOS native Unicorn requires
JIT access outside the restrictive sandbox. Execution stubs provide allocation,
copy/fill, role, clock, policy, queue, GUI, connection state, and lower BLE calls;
logging is disabled. It does not prove RTOS scheduling, complete GUI or radio
behavior, large/invalid-length safety, or source/byte equivalence. Pseudocode
uses conceptual native structs; only the interface header is intended for host
reuse. No firmware patch, hardware access, commit, or shared gate update occurred.

Next useful bounded work: trace queued ring TX discard/cancellation paths and
actual task configuration before designing the exact ownership change; for app
understanding, resolve active-page click callbacks beyond dashboard scrolling.
