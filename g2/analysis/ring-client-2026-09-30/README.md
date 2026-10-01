# G2 R1 BLE client: seven functions explained

This batch closes the G2-side ring UUID gap and recovers the client lifecycle,
receive filtering, delayed notification enablement, and transmit queue contract.
It covers **seven functions / 1,446 bytes**, `0x004C46C0..0x004C4C66`, in official
`s200_v2.2.6.10`. It is manually recovered behavioral pseudocode, not original
source, a firmware build, or a byte-matched implementation.

## Deliverables

- [ring_client.pseudocode.c](ring_client.pseudocode.c): readable seven-function
  recovery, with stock addresses, conceptual data layouts, callers and external
  dependencies. Diagnostic logging is omitted. Syntax checked as C11.
- [ring_client.h](ring_client.h): reusable UUID constants, stock default handles,
  and epoch-token helper for app/simulator development.
- [disassembly.txt](disassembly.txt): fresh Capstone decode of every function byte,
  with named direct call targets and matching stock function hashes.
- [validation.json](validation.json): **25 passing scenarios running the original
  Thumb instructions**, plus per-function hashes, instruction-verified direct
  callers, UUID bytes and discovery descriptor addresses.
- [verify.py](verify.py): bounded offline reproduction. External BLE, RTOS,
  allocation, logging and event-loop calls are stubs; the seven function bodies
  execute from the official firmware. It writes only this directory's disassembly
  and validation report. It does not run the handwritten C pseudocode.

## Newly pinned interface

The earlier [protocol reference](../../docs/reference/protocols.md#12-r1-ring-link-as-seen-from-g2)
explicitly left G2's R1 service identity unpinned. The original discovery function
at `0x004C487C` loads the service pointer from literal `0x004C4C98` and calls
`0x005332B4` with six arguments:

```c
app_discover_service(conn, 16, (void *)0x007880B0, 3,
                     (void *)0x200030D8, result_handles);
```

The last two arguments are stack arguments at BL `0x004C48A6`; the old raw Ghidra
call expression omitted them. Original-code execution confirms all six.

| Role selected by G2 | UUID | Constant address |
|---|---|---|
| R1 service | `BAE80001-4F05-4503-8E65-3AF1F7329D1F` | `0x007880B0` |
| Write characteristic | `BAE80010-4F05-4503-8E65-3AF1F7329D1F` | `0x007880C0` |
| Notify characteristic | `BAE80011-4F05-4503-8E65-3AF1F7329D1F` | `0x007880D0` |
| Client characteristic configuration | `0x2902` | `0x0078F540` |

128-bit UUID bytes are stored least-significant byte first: the service is
`1f9d32f7f13a658e0345054f0100e8ba`. The SRAM discovery pointer array at
`0x200030D8` contains `0x0078DFCC`, `0x0078DFD4`, `0x0078DFDC`; those flash records
point to the two characteristic UUIDs and the CCC UUID above. Their remaining
four bytes are respectively `03 00 00 00`, `03 00 00 00`, `06 00 00 00`;
this batch does not assign undocumented meanings to those flag fields.

The SRAM array was read from the existing fixed initializer replay output,
17,752 bytes, SHA-256
`df1a1fdf7b2792a7c4ef7a2c5cc6d1423bc7833b556fdfcedb8d6d927fbbb743`,
at offset `0x30D8`. These 12 bytes are `ccdf7800d4df7800dcdf7800`.
The verifier authenticates that decoded file before reading it; the array is
not misidentified compressed flash bytes. Its source/replay provenance is in
`g2/build/pseudocode-first/20260930T190500Z/attempts/P1-apollo-main-canonical-replay-009/001/execution-receipt.json`.
The isolated discovery execution verifies the pointer passed, not the stack's
complete discovery traversal. Descriptor roles are also supported by the client
handle consumers below.

## Behavior useful to apps, patches and a simulator

**Connection and notification setup.** Init and central connection-open both
write handle defaults `{0x0010,0x0012,0x0013}` for write, notification and CCC.
These are stock defaults, not universal handles to hardcode into another client.
Open increments a 16-bit epoch and schedules the same callback with delays
500/700/900 (scheduler units; this batch does not establish the timebase).
All three callbacks write notification-enable bytes `01 00` to the **same CCC**.
The three discovery entries are not three notification descriptors.

Each callback checks nonzero connection, active connection ID, matching epoch,
`DmConnInUse`, and nonzero CCC. Its token is
`(epoch << 16) | (final_attempt << 8) | conn`. Close clears the connection and
handles, increments the epoch, removes delayed callbacks and emits ring event 8.
The epoch wraps modulo 65,536. This matters when reproducing reconnect behavior.

**Readiness nuance.** The final delayed attempt emits ring event 4 immediately
following `AttcWriteReq`; it does not wait for or inspect an ATT response in this
function. Event 4 is therefore not, by itself, proof that the peer accepted the
CCC write. Consumers of event 4 need their own inspection before labeling it
“notifications confirmed.”

**Receive path.** Events `0x05`, `0x0D`, `0x0E` enter the handler only when
`DmConnRole(active_conn)==0`. Status must be zero and the message's ATT handle
must match the notification handle. The payload pointer and u16 length then go
to `Thread_SendMsgToRingTaskWithId`. The local body does not compare the message
connection ID with the active connection ID; an offline mismatched-ID case
still forwards. This is a local routing observation, not evidence of a remotely
reachable defect: upstream event routing was not recovered in this batch.

**Transmit path.** `APP_BleRingSendDataMsg` waits for TX readiness, allocates a
12-byte WSF message, stores event `0xAC`, connection, **borrowed payload pointer**
and u16 length, and queues it. There is no payload copy here. It returns zero
on success, disconnected drops and allocation failure. Allocation failure
releases TX readiness; the disconnected early path never acquires it.
The queued event handler checks connection equality and a nonzero write handle,
then calls `AttcWriteCmd`; stale queued messages release readiness instead.
Buffer lifetime, successful TX completion and synchronization require examining
the wait/notify providers and the callers—not assuming zero means delivery.

## Function map

| Entry | Recovered responsibility |
|---|---|
| `0x004C46C0` | Pack connection/final-attempt/epoch token |
| `0x004C46D0` | Reject stale callback; write CCC; optionally emit event 4 |
| `0x004C4810` | Initialize client state and default handles |
| `0x004C487C` | Start discovery with service UUID and three-item list |
| `0x004C48AC` | Filter status/handle and forward received data |
| `0x004C4910` | Dispatch open, close, RX and queued TX events |
| `0x004C4B7E` | Queue outbound borrowed buffer; handle allocation failure |

Direct callers/callees and exact callsites are in `validation.json`; that list
is nonexhaustive and does not claim indirect-call closure. The existing Ghidra
exports under `g2/research/corpus/apollo-main/ghidra/open-2026-09-29/decomp/`
seeded the reading; source instructions and emulator cases checked it.

## Validation and limits

Input `g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin` is exactly
3,523,396 bytes, SHA-256
`36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863`.
Runtime address = file offset + `0x00437FE0`; the first 32 bytes are the OTA
preamble, vectors/code begin at `0x00438000`. All seven function slices match
the existing stock hashes. Decode mode is little-endian Arm Thumb/M-class.

```sh
~/.local/share/opencfw/venv/bin/python g2/analysis/ring-client-2026-09-30/verify.py
clang -std=c11 -Wall -Wextra -fsyntax-only g2/analysis/ring-client-2026-09-30/ring_client.pseudocode.c
```

The Python verifier requires installed Capstone/Unicorn and the existing pinned
17,752-byte initializer output mentioned above. macOS Unicorn native JIT needed
execution outside the restrictive sandbox (sandbox run trapped at `mem_map`;
the approved offline run passed). No tools or native libraries were changed.
It tests init, discovery arguments, token packing, stale/wrong/zero connections,
closed connections, missing CCC, open/close/epoch wrap, peripheral filtering,
RX status/handle filtering, wrong-ID local RX, queued TX and allocation failure.
No radio, hardware, whole-firmware boot, actual scheduler delay or concurrency
behavior is simulated; logging is disabled and external provider semantics
are assumed through explicit stubs. The C is syntax checked, not linked or
proved equivalent over every input.

Next useful batch: follow `Thread_SendMsgToRingTaskWithId` (`0x004C548C`) into
`ring_service.c` (`0x00472244..0x00472C7C`) to recover packet layouts for commands
`0x61/0x85/0x8A/0x8B/0x8C/0x94/0x96`, event-4 consumers and TX buffer lifetime.
This would turn the recovered BLE carrier into a practical ring protocol model.

All outputs are new, Git-visible files in this directory. The active inventory
campaign, shared state/gates, staged changes and historical corpus were not
modified. This work follows the user's request to prioritize useful bounded
pseudocode and understanding; it claims no global workflow gate completion.
