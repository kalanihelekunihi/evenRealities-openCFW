# Ring command payloads and buffer ownership

This extends the [ring-client batch](../ring-client-2026-09-30/README.md) with
five outbound command formats, all seven RX dispatcher command IDs, the
heap-owned RX queue, and the TX readiness/lifetime path. **42 bounded tests
execute original firmware instructions.** Nine packets produced by the reusable
C header match packets captured from those executions.

The useful distinction is now concrete: **RX copies and owns its payload;
TX borrows an encoder's stack storage.** A controlled delayed-consumer test
shows the first queued TX reading the second encoder call's bytes. This is a
reproducible lifetime risk under the specified synthetic schedule, not a claim
that the real RTOS/hardware routinely exhibits it.

## Deliverables and scope

- [ring_service.pseudocode.c](ring_service.pseudocode.c): 19 readable function
  recoveries, plus three clearly labeled supporting excerpts. Logging omitted;
  external providers are declarations. Syntax checked as C11.
- [ring_protocol.h](ring_protocol.h): five side-effect-free packet builders,
  conservative minimum-length checks, and timestamp decoding for app/simulator
  use. Not firmware source reconstruction or an on-device patch.
- [disassembly.txt](disassembly.txt): fresh Thumb decode of 22 inspected bodies,
  4,206 bytes, with direct-call addresses and body hashes. Three prior-batch
  client bodies also execute in the integrated tests but are not new coverage.
- [validation.json](validation.json): all 42 original-code scenarios and their
  observed calls/data; [verify.py](verify.py) reproduces them offline.
- [test_header.c](test_header.c): host C vectors and conservative bounds checks.

## G2 → ring packets

Each row is the entire byte sequence supplied to `APP_BleRingSendDataMsg`.
No length, checksum, framing or encryption field is added by these encoders.
The lower BLE stack's transport mechanics are outside this statement.
The meanings of prefix bytes `00 1A` and `00 35` are not established here.

| Operation | Bytes | Original entry |
|---|---|---|
| Glasses heartbeat | `00 1A 94 01` | `0x00472244` |
| Touch algorithm report interval, normal public path | `00 1A 8A 01 hi lo` | wrapper `0x00472362`, consumer `0x004C4DE8`, encoder `0x004722D8` |
| Enable ring touch | `00 1A 85 01 00 AA AA AA` | `0x00472378` |
| Disable ring touch | `00 1A 85 01 FF AA AA AA` | `0x00472378` |
| Glasses status flags | `00 1A 89 01 flags 00 00 00` | `0x004723D6` |
| Command `0x88`, meaning left open | `00 35 88 00` | `0x00472546` |

For `0x89`, `flags = (arg0 << 7) | (arg1 << 6)`, truncated to a byte. The
reusable header takes Boolean arguments; stock shifts raw bytes. The upstream
status policy references in-case, wear, IMU and LCD states, but this batch does
not prove a complete interpretation of each resulting flag.

**Interval endianness matters.** Calling the low-level encoder with `0x1234`
produces `00 1A 8A 01 34 12`. The public wrapper copies the u16 into an owned task
message in little-endian order; its consumer combines those bytes as a
big-endian integer before calling the encoder. That full original-code path
produces `00 1A 8A 01 12 34`. The header implements the normal public path.
The report interval's physical unit is not established by this batch.

## Ring → G2 dispatch

`RING_CmdPackageParse` at `0x00472988` selects solely on byte 2. There is no
common null, length, prefix or checksum check in that body. Byte 3's meaning is
command-specific; do not treat it as one universal status field.

| Command | Fields read / observed behavior |
|---|---|
| `0x61` touch | byte 3 must be zero to emit an input event; byte 4 type; bytes 5–6 extra values for types 4/5; optional u32 LE at bytes 7–10 |
| `0x85` HID/touch-enable acknowledgement | remove two retry callbacks; publish ready locally on owner side, otherwise notify phone; helper logs success only for bytes 3/4 equal to 1. Ready-side effects happen before that log-only check. |
| `0x8A` report-interval acknowledgement | diagnostic only |
| `0x8B` battery | requires at least six bytes; byte 4 battery, byte 5 charging (diagnostic names); forwards an 8-byte device-manager record beginning `04 00 02 00 battery charge` |
| `0x8C` wear | Boolean byte 4; on transition to worn record kernel tick; on removal report elapsed ticks under telemetry key `0x60102` |
| `0x94` heartbeat response | byte 4 `0x20` or `0x40` logs a touch/ATI error and schedules disable/enable callbacks at +100/+500 ticks; other values log success |
| `0x96` invalid glasses MAC | retrieves the currently configured ring MAC and calls unpair cleanup; it does not take a replacement MAC from this packet |

The references' short command summary must not be interpreted as a positional
mapping: **battery is `0x8B`, wear is `0x8C`, heartbeat is `0x94`.** Packet
`0x89` is outbound glasses status and does not appear in this RX dispatcher.

Touch type → internal input event (`source=4`):

| Ring type | Internal event | Additional arguments |
|---|---|---|
| 0 | 3 | 0, 0 |
| 1 | 0 | 0, 0 |
| 2 | 1 | 0, 0 |
| 4 | 5 | packet bytes 5, 6 |
| 5 | 4 | packet bytes 5, 6 |
| 8 | 14 | 0, 0 |

Gesture names are intentionally not invented from these integers. With the
optional timestamp present, all types except 8 are suppressed if the previous
timestamp is nonzero and unsigned 32-bit delta is below 100. Exactly 100 passes;
wraparound arithmetic is tested. The peer timestamp's unit remains unknown.
The timestamp is updated before checking byte 3, even for nonzero byte 3.

**Bounds discrepancy:** `RING_CmdTouchUpdate` checks `length > 7` but loads a
u32 at offset 7, requiring 11 bytes. An original-code test with declared length
8 and padded backing memory confirms reads through offset 10. This is not a
hardware reachability/exploit claim. The reusable helper rejects lengths 8–10
and requires at least seven bytes for the short touch form. These are tooling
checks, deliberately stronger than stock; prefix/authentication remains the
caller's responsibility. Battery has a real six-byte guard; the other handlers
lack a common minimum-size guard in this recovered path.

## Ownership and scheduling

RX path:

```text
Thread_SendMsgToRingTaskWithId (0x004C548C)
  → ring_task_msg_send (0x004C549C)
    allocate 8 + length bytes
    write {u32 id=2, u32 length, inline payload COPY}
    queue pointer, wake ring thread (flag 0x400000)
  → _thread_msg_handler (0x004C4DE8)
    parse inline copy, then free allocation
```

Null data with nonzero length, missing queue and allocation failure return -1.
Queue-put failure frees the allocation and returns -1. A test overwrites the
original caller buffer after enqueue and still observes the original battery
bytes at the parser, followed by the matching free.

TX path:

```text
ring command encoder's stack buffer
  → APP_BleRingSendDataMsg (previous batch, 0x004C4B7E)
    wait-before-send; allocate only 12-byte WSF envelope
    store caller's pointer; queue envelope
  → WsfMsgSend (0x004BF9BA)
    enqueue envelope, mark task ready, return (no data copy / completion wait)
  → encoder returns, invalidating its stack-buffer lifetime
  → APP_BleRingProcMsg / AttcWriteCmd eventually reads the pointer
```

`threadBleWsfTakeTxReady` (`0x004D0B36`) wraps a semaphore acquire.
`thread_ble_wsf_wait_tx_ready` (`0x004D0B64`) first tries timeout zero, then at
most 20 acquisitions with timeout 10 and `osDelay(10)` after failures. It still
returns after all failures. It waits before queueing and does not wait for
consumption of the newly queued buffer. Completion notify (`0x004D0C36`)
releases one token only when a semaphore exists and its count is zero.

In `delayed_consumer_reads_reused_stack_payload`, semaphore acquisition is
stubbed to fail and WSF dispatch is deliberately delayed:

1. Original interval encoder queues `00 1A 8A 01 34 12` at stack pointer
   `0x200FEEF0`, then returns.
2. A second original call queues `00 1A 8A 01 78 56` at the same payload address,
   using a different WSF envelope.
3. Dispatching the first envelope calls `AttcWriteCmd` with the **second** packet.

All encoder, send, wait and WSF send bodies in that chain are original code;
semaphore/queue providers and dispatch timing are synthetic. Real task priorities
and preemption may change the outcome. Practical patch direction: give TX an
owned copy lasting through lower-stack consumption, define its release point,
and return a meaningful queueing error. Merely waiting before send does not
establish ownership. No such patch was applied in this analysis.

**Delayed values are kernel ticks.** Original `fw_event_loop_push_delayed`
(`0x0047697E`) stores `tick_now - epoch_base + delay_argument`. An execution test
with now=1000, base=100 and argument=500 stores deadline 1400. This proves the
unit relationship without assuming a tick frequency. Existing library notes
report 1024 Hz, but this batch does not independently revalidate that clock and
therefore does not relabel the arguments as milliseconds. Wear duration likewise
uses raw kernel ticks even though its retained log format says `ms`.

Ring event 4 from the previous batch schedules three callbacks at +200, +500 and
+3000 ticks (`0x004C5033`, `0x004C4EE5`, `0x004A285D` respectively). This is setup
scheduling, not a check that the CCC write succeeded.

## Provenance and reproduction

Official input: `g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin`,
3,523,396 bytes, SHA-256
`36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863`.
Runtime address = file offset + `0x00437FE0`; the first 32 bytes are a preamble,
not code. Execution/decode uses Arm Thumb/M-class, little-endian.

Body boundaries/hashes come from `g2/symbols/apollo_main.tsv`, except heartbeat
`0x00472244`: that seed has no hash and includes a literal tail. Its authenticated
raw Ghidra function record ends at `0x004722CC` and has SHA-256
`ab5edc901c7263a3db6b6b917d48681827bf31706d1d3db2e06e9cdebccb2844`.
The verifier uses that body, not the seed's `0x004722D8` boundary. Original
Ghidra exports under `g2/research/corpus/apollo-main/ghidra/open-2026-09-29/`
seeded reading; fresh disassembly, byte checks and execution support this report.
No compressed regions or toolchain dependencies are counted as firmware code.

```sh
~/.local/share/opencfw/venv/bin/python g2/analysis/ring-protocol-2026-09-30/verify.py
clang -std=c11 -Wall -Wextra -fsyntax-only g2/analysis/ring-protocol-2026-09-30/ring_service.pseudocode.c
clang -std=c11 -Wall -Wextra -Werror g2/analysis/ring-protocol-2026-09-30/test_header.c -o /tmp/opencfw-ring-protocol-header-test
/tmp/opencfw-ring-protocol-header-test
```

The host test prints nine named vectors. Each was compared with the `send.packet`
field of the identically named original-code case in `validation.json`: all
matched; conservative bounds assertions passed. The Python verifier requires
installed Capstone/Unicorn, and macOS native JIT access outside the restrictive
sandbox. It depends on the locked firmware and tracked references, not an
ignored initializer output. No hardware, BLE connection or network is used.

Execution stubs are explicit in `verify.py`; logging is disabled. Tests do not
prove RTOS scheduling, radio outcomes, general parser safety, whole-firmware
boot, or handwritten-C equivalence over every input. Supporting functions are
only exercised on the paths stated. Existing shared campaign/state and prior
artifacts were not changed, and no source-completeness gate is claimed.

Next useful batch: resolve `input_event` at `0x004C5916` into named gesture/app
actions, then validate the proposed owned-TX lifetime against the lower ATT
copy/release path and actual task priorities. Those facts would support a
specific safe CFW change rather than merely describing the lifetime risk.
