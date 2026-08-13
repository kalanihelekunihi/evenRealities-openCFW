# Scalar-health offline-sync correlation

## Outcome

Heart rate, blood oxygen, and heart-rate variability each use a product-owned 24-entry offline
FIFO between their daily aggregate caches and the already-admitted public history synchronizers.
No signal-processing algorithm is present in this family: the functions queue completed hourly
minimum/average/maximum values, assemble day packets, and retire acknowledged records. The clean
implementation therefore owns only R1-specific storage and synchronization policy; Goodix and
other sensor or algorithm providers remain outside this boundary.

## Recovered boundaries

| Metric | Consume | Empty | Enqueue | ACK | Merge |
| --- | --- | --- | --- | --- | --- |
| heart rate | `0x0003FAA4..<0x0003FB32` | `0x0003FB90..<0x0003FB9E` | `0x0003FBA4..<0x0003FC5E` | `0x0003FCEC..<0x0003FDFC` | `0x00040700..<0x00040832` |
| HRV | `0x00040984..<0x00040A18` | `0x00040A74..<0x00040A82` | `0x00040A88..<0x00040B46` | `0x00040BD4..<0x00040CE4` | `0x00041638..<0x00041768` |
| SpO2 | `0x00043CA0..<0x00043D2E` | `0x00043D90..<0x00043D9E` | `0x00043DA4..<0x00043E5E` | `0x00043EB0..<0x00043FC0` | `0x000448B0..<0x000449E2` |

Ghidra omitted the three 272-byte acknowledgement callbacks from its function inventory. Their
stored Thumb callback pointers, prologues, complete control flow, returns/tail calls, and following
literal pools establish exact extents. They are recorded as manual provenance supplements. The
other twelve bodies come from `functions.csv`; the verifier pins every body by size and SHA-256.

## Exact storage formats

Heart rate uses metadata at `0x20006798` and records at `0x2001576C`; SpO2 uses metadata at
`0x2000679B` and records at `0x200158EC`. Both have 24 records of exactly 16 bytes:

| Offset | Width | Meaning |
| ---: | ---: | --- |
| `0x00` | 1 | average |
| `0x01` | 1 | maximum |
| `0x02` | 1 | minimum |
| `0x03` | 1 | retained byte, not initialized on reuse |
| `0x04` | 4 | local-day start timestamp |
| `0x08` | 4 | recorded timestamp |
| `0x0C` | 2 | signed UTC offset in minutes |
| `0x0E` | 1 | hour index, `0...23` |
| `0x0F` | 1 | retained byte, not initialized on reuse |

HRV uses metadata at `0x200067AB` and records at `0x2001636C`. Its 24 records are exactly 20 bytes:

| Offset | Width | Meaning |
| ---: | ---: | --- |
| `0x00` | 2 | average RMSSD aggregate |
| `0x02` | 2 | maximum |
| `0x04` | 2 | minimum |
| `0x06` | 2 | retained bytes, not initialized on reuse |
| `0x08` | 4 | local-day start timestamp |
| `0x0C` | 4 | recorded timestamp |
| `0x10` | 2 | signed UTC offset in minutes |
| `0x12` | 1 | hour index, `0...23` |
| `0x13` | 1 | retained byte, not initialized on reuse |

Each metadata triple is read index, write index, and count. Enqueue rejects a zero average, a
future recorded timestamp, or a future day start. A full ring advances the oldest read index while
remaining at count 24. Consumption clears only the consecutive oldest prefix whose recorded
timestamps do not exceed the cutoff.

Merge walks FIFO order and skips zero or future records. A change in day start or UTC offset
flushes the current packet, so separated runs with the same key remain separate packets. Repeated
hours replace the prior aggregate without increasing the slot count. The acknowledgement value
for a packet is its largest accepted recorded timestamp. Serialization reuses the established
UInt8 and UInt16 daily encoders rather than introducing a private wire format.

## Acknowledgement distinction

Modes zero and two update the metric's persistent cursor only when the acknowledgement is no later
than the sampled firmware time and newer than the cursor. Mode one consumes the offline FIFO
prefix even when its cutoff would be future relative to the current clock. Unknown modes preserve
both cursor and queue.

The heart-rate and SpO2 callbacks sample the firmware clock before discriminating every non-null
mode. The HRV callback switches first and samples the clock only for modes zero and two; its mode
one path directly consumes the queue. `r1_health_offline_ack_result.firmware_clock_sampled`
preserves this otherwise subtle observable difference.

## Clean implementation and hardening

`r1_health_u8_offline_queue` is the shared byte-aggregate engine used by distinct heart-rate and
SpO2 state instances. `r1_health_u16_offline_queue` preserves HRV's wider records and distinct ACK
clock policy. Both require caller-owned packet workspace and an emission callback, avoiding hidden
allocation and large transient task stacks.

The clean implementation validates the metadata invariant and every active hour index before
access. Corrupt state returns `R1_ERROR_STATE` instead of indexing outside the queue or day packet.
Tests cover both exact record sizes, all retained bytes, all enqueue drop reasons, full-ring
overwrite, FIFO-prefix consumption, repeated-hour replacement, future filtering, exact UInt8 and
UInt16 packet bytes, metric-independent state, ACK clock policy, and corrupt-state rejection.

The retained `.openr1_health_api` link seam makes all ten portable queue operations independently
auditable in the unsigned Nordic application. The UInt8 operations link at `0x00033A1E`,
`0x00033A42`, `0x00033DA4`, `0x00033E76`, and `0x00034096`; the UInt16 operations link at
`0x00033A30`, `0x00033BEC`, `0x00033E08`, `0x00033F7A`, and `0x00034108`. The retained table is at
`0x0003B274`. The application is 90,956 bytes text, 236 bytes data, and 132,456 bytes BSS. Its HEX
and BIN SHA-256 values are `0954a9375874ee4f88139ba6243e20e1afba122e67afccba9d410e638053fa81`
and `31f3a97de9805239b03c51297f1de2ea9eaeff6fee372f1ea1f0c0a5c2f7bc91`.

This boundary adds no private SRAM reader, internal
event injector, sensor algorithm, BLE command, signing bypass, or deployment change.
