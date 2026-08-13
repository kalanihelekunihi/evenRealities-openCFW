# 280...308-byte frontier correlation

The next five largest unresolved application functions are now source-routed from immutable body
hashes, complete direct-call scans, and function-local control-flow review:

| Recovered function | Executable bytes | SHA-256 | Disposition |
| --- | ---: | --- | --- |
| `0x00065B4C..<0x00065C80` | 308 | `6f6af2221a4b1479db34b88f6b57c9dec3f0153351637ba8fdc867c69741e11e` | R1 delayed-event scheduler |
| `0x00033850..<0x00033982` | 306 | `034f58f9537b96a7c9f0c0ff0c78924bb810dd8a5984bca8d51c82b17b25ecdf` | R1 BLE-thread envelope |
| `0x00029D5C..<0x00029E88` | 300 | `5d0234e082228ae93c477e354bebf963d0e8b5912b75794be21d186c276ffb7c` | Goodix licensed-provider boundary |
| `0x00083F24..<0x00084050` | 300 | `f214c7da6cdac32ec60cfad2dbd36ac2564c6bde7da1139aab0e74ad1141a23c` | R1 health-settings command planner |
| `0x00032598..<0x000326B2` | 282 | `08fbc118a7e78dbc5d62af22c60f8566677788a25ddc42446ec0e89dc6914b9b` | R1 `pb_tran` fragmenter |

The Ghidra inventory reports 280 bytes for `0x00032598` while its inclusive end and the recovered
disassembly continue through the two-byte back-edge at `0x000326B0`. The independently verified
executable extent is therefore 282 bytes. The summarizer retains both values and pins the complete
body.

## Product-owned behavior

`0x00065B4C` has 44 direct callers across the product runtime. Delays below two milliseconds are
sent to the immediate event path. Longer delays acquire the event-loop seam, take the first empty
slot in a 64-entry table, store event/context and delay plus elapsed timer time, wake the worker,
and invoke the already closed timer step with a `0xFFxxxxxx` elapsed override. The clean
`r1_delayed_event_schedule` API reproduces the deterministic table and timer transition and
returns typed immediate/wakeup actions. CMSIS mutexes, thread flags, initialization waits, live
ticks, logging, and the actual immediate queue stay in their providers/platform adapter.

`0x00033850` has six direct callers. It rejects a null payload with nonzero length, allocates
`(payload_length + 15) & ~3`, writes three UInt32LE words (message type, context, payload length),
copies the payload at byte 12, performs a no-wait queue put, frees on failure, and wakes the BLE
thread. This is the same deterministic envelope already implemented by
`r1_ble_thread_message_encode`; allocation, FreeRTOS/CMSIS queueing, thread wakeup, and cleanup
remain external.

`0x00083F24` is the method-sensitive system `01/00/0E` handler reached through a registration
table, so it has no direct branch caller. Read returns exactly 12 bytes: UInt32LE persisted
timestamp, normalized health-enable byte, and seven zero bytes. Set acknowledges before effects,
compares the requested raw byte with stored normalized state, normalizes any nonzero value to
enabled for persistence, and publishes the raw byte on private event `0x100D` when the raw values
differ. A noncanonical `1 -> 2` request therefore publishes the event but does not rewrite the
timestamp because the inner normalized persistence check sees no state change. The clean planner
models this observable edge while requiring a canonical 12-byte payload. It performs no storage,
private-event emission, GoMore control, or sensor action.

`0x00032598` is called at `0x0004E82C` from the generic export path. It accepts at most 4,096
bytes, computes the existing non-reflected CRC-32C (polynomial `0x1EDC6F41`, initial zero, no final
XOR), and emits descending sequence fragments. Each fragment contains sequence, UInt32LE CRC,
one channel byte, and at most 238 payload bytes, for a 244-byte maximum. Exact multiples retain a
six-byte empty terminal fragment; 4,096 bytes require 18 fragments. `r1_pb_fragment_message`
implements only this bounded encoding and does not expose the private virtual-file reader or live
transport.

## Provider boundary

`0x00029D5C` is called only at `0x0002A856` inside the already gated GH3X2X provider. It updates
private per-channel decimation state and rolling windows and calls an adjacent Goodix processing
helper. Its signal-processing state, coefficients, thresholds, and private ABI remain
`goodix_gh3x2x_candidate`; no local substitute or reconstruction is admitted without matching
licensed provider source.

Reproduce with:

```sh
python3 tools/evidence/summarize_r1_frontier_280_308.py
python3 tools/build_r1_source_ownership.py --check
python3 tools/verify_openr1.py
```

The three newly retained clean-room APIs link at `0x00032528`, `0x00033DE2`, and `0x00036466` in
the unsigned Nordic application. It contains 94,804 bytes of text, 236 bytes of data, and 132,544
bytes of BSS. The 95,040-byte BIN has SHA-256
`421a42cf37dad04dadcff5d3b1742efcba4ba50fd1d2e52f26bcf00e5df24d35`; the standalone HEX has
SHA-256 `48e1b3fadfdb956fbdf5f637d48c9a5808db5394848fb4538450c0ff98be80cf`.
Code signing, deployment authorization, keys, vendor security checks, and bypasses remain outside
this closure.
