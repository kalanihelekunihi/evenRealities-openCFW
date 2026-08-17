# GoMore topic-input and readiness correlation

## Result

The four recovered GoMore sensor callbacks and their shared readiness barrier are now explicit,
bounded C in `reconstructed/gomore_primitives/`. The source-built Zephyr target can register the
exact `"gomore"` rate-1 batch listener on the existing `"acc"` stream and stage its normalized
25-sample input. That listener is dormant: startup does not register it, no BLE command enables
it, and it does not run the health engine or publish biometric output.

The `"raw_hr"`, `"hr"`, and `"hrv"` callback reducers also compile and are host-tested. The exact
stock `raw_hr` scalar accumulator now compiles too, preserving its 124-byte count/reserved/value
record without assigning waveform semantics. The Goodix demo callback supplies an array of physical
channels, while the stock callback receives one already-selected UInt32 per call; evidence does not
yet prove that selection. The target therefore does not connect those callbacks or fabricate the
remaining stream sources.

## Pinned image evidence

Stock application load base: `0x00027000`. Rebuilt image SHA-256:
`0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a`.

| Extent | Bytes | SHA-256 | Reconstructed behavior |
| --- | ---: | --- | --- |
| `0x00049410..<0x0004960A` | 506 | `a5898f09a8c50776e5f37aa43887223d989544b89ad9c5408489a73c5456407b` | seven-slot authorization and exact `acc`, `raw_hr`, `hr`, `hrv` listener lifecycle |
| `0x0006ACC8..<0x0006ACD2` | 10 | `3badaeb80fceb23c967ef58d3c3da3c18870fba79034fd608da8659c586a927f` | clear acc/raw counts after a successful engine update |
| `0x0006B0D4..<0x0006B10E` | 58 | `8f159dceef23f9d294812d1b330e4b31335d6965de6393f3e06d908dfd9f1db2` | required-input readiness barrier and ready-byte clear |
| `0x0006B114..<0x0006B1B8` | 164 | `12d48128ccaab3563434e1020cafeae53af5c37848aa5e7df228776cfd3139e4` | accelerometer batch callback |
| `0x0006B1B8..<0x0006B1F4` | 60 | `74acdce104fa24422fcb4b7101bb6a70c143d3442bb4fe23f8fe94ad21687eed` | direct-heart-rate callback |
| `0x0006B1F4..<0x0006B228` | 52 | `bf19893965dc98b713fe3c861943ce8505cfe4434b2cacfa44a6c69133770e8f` | four-value HRV auxiliary callback |
| `0x0006B228..<0x0006B272` | 74 | `ab337651b4344af149b261e8c0e733690a02df92bffcb5b79ee4370e7b8b3134` | raw-optical callback |
| `0x0008A01C..<0x0008A038` | 28 | `6d8e91f9572f177c80454d8fdad3aecc847c74495e9636859a28825b330de651` | bounded scalar append into the 124-byte `raw_hr` record |

The manager's literal pool proves the exact registrations, all at rate 1 and batch mode 0:

| Stream | Listener | Callback pointer |
| --- | --- | --- |
| `acc` | `gomore` | `0x0006B115` |
| `raw_hr` | `gomore` | `0x0006B229` |
| `hr` | `gomore` | `0x0006B1B9` |
| `hrv` | `gomore` | `0x0006B1F5` |

Ghidra omitted all six callback/readiness/cleanup entries from its function CSV. The acc and
raw-optical callbacks were already manual provenance supplements; the widened Thumb-entry census
now adds the direct-HR and HRV callbacks plus the readiness and successful-update bookkeeping, so
every extent in this adapter path has an explicit ownership row.

## Exact portable contracts

- Accelerometer input is the existing 188-byte batch. Stock reads the low count byte at offset
  180, clamps to 25, and consumes six-byte signed XYZ records. Algorithm axes are
  `-Y * 0.9765625`, `X * 0.9765625`, and `Z * 0.9765625`; the Float32 scale word is
  `0x3F7A0000`. The callback sets ready bit `0x01`.
- Raw optical input starts with a UInt8 count, clamps to 25, then converts UInt32LE values at
  offset 4 to Float32. It sets ready bit `0x02`.
- The stock producer accepts a single UInt32 per call. While count is below 30 it writes the value
  little-endian at `4 + count * 4`, increments only byte 0, and preserves reserved bytes 1...3 and
  every unused slot. At count 30 or above it performs no write. `r1_goodix_raw_hr_append` adds NULL
  rejection and an appended/not-appended return without changing accepted-input state.
- Direct HR converts byte 0 to Float32 and sets ready bit `0x04`. That bit is opportunistic and
  does not participate in the worker barrier.
- HRV reads its count at byte 9, clamps to four, clears the eight-byte auxiliary buffer, and copies
  that many UInt16LE values from byte 0. It sets no readiness bit and the recovered host-to-engine
  adapter does not consume this lane.
- The worker may run when every currently required acc/raw input is ready. It then clears the
  complete ready byte, including opportunistic HR. Neither input required means no update.
- Only a successful engine update clears the staged acc/raw sample counts. HR and HRV state
  persist until their separate stream teardown paths.

## Safety-preserving divergences

The stock acc and raw-optical callbacks dereference their payload before checking it. The C
reducers validate pointers and complete lengths first and do not mutate state on malformed input.
The stock HRV callback overwrites an over-limit count byte in its caller's buffer; the transparent
reducer clamps into owned state without modifying the input packet. These changes remove memory
hazards without changing accepted-input results.

## Verification and runtime boundary

Host tests cover the exact axis order/scale, 25/4 clamps, packet offsets, UInt32/UInt16 conversion,
all three readiness bits, single- and dual-required barriers, successful versus failed cleanup,
and malformed-input immutability. The Zephyr source-boundary verifier requires the exact `gomore`
batch registration and rejects any startup call that would activate it.

This closes the transparent topic-input reduction, scalar `raw_hr` accumulator, and the available accelerometer staging seam.
It does not claim GoMore result quality, physical-axis correctness, a live Goodix raw-optical
producer, or a validated health-engine configuration. Those remain separate composition and
owned-hardware gates.
