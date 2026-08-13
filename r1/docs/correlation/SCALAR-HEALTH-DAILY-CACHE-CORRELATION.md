# Scalar-health daily-cache correlation

## Outcome

Nine product-owned callbacks adapt heart-rate, blood-oxygen, and heart-rate-variability hourly
aggregates to the daily storage interface. They perform cache bookkeeping and exceptional
pre-time-sync recovery only; no biometric signal processing, sensor register logic, Goodix code,
or other third-party algorithm appears in these bodies. OpenR1 implements the behavior over
caller-owned state and routes fallback records through the already admitted scalar offline queues.

| Metric | Reset | Read | Write | Aggregate width |
| --- | --- | --- | --- | ---: |
| heart rate | `0x0007062C..<0x00070646` | `0x00070648..<0x000706A0` | `0x000706A4..<0x000706BE` | 3 bytes |
| HRV | `0x000706BE..<0x000706D8` | `0x000706D8..<0x00070736` | `0x0007073C..<0x00070758` | 6 bytes |
| SpO2 | `0x00090DD4..<0x00090DEE` | `0x00090DF0..<0x00090E48` | `0x00090E4C..<0x00090E66` | 3 bytes |

Every body is taken from the Ghidra function inventory and pinned by its exact size and SHA-256 in
the verifier. Heart rate and SpO2 have independent callback addresses, SRAM roots, FIFO instances,
and synchronization cursors even though their three-byte aggregate representation is identical.
OpenR1 shares only a bounded UInt8 cache engine between those two independent state instances.
HRV uses a separate UInt16 engine and 20-byte offline records.

## Reset and write behavior

The heart-rate and SpO2 caches each contain 24 `[average, maximum, minimum]` UInt8 slots followed
by signed UTC offset, a reserved byte, a five-byte latest point, and local-day start. HRV contains
24 UInt16LE triples followed by signed UTC offset, padding/latest-point bytes, and local-day start.
Each reset clears only the aggregate slots, replaces UTC offset and day, and preserves its latest
point and intervening bytes. In OpenR1 the latest point is a separate typed field, so the reset
clears normalized slot/rolling state while preserving `latest_value`, `latest_timestamp`, and
`has_latest`.

Write replaces only average, maximum, and minimum for one slot. The stock callbacks do not validate
their index before calculating a cache address; the portable counterparts require `0...23` and
return `R1_ERROR_LENGTH` otherwise. They do not mutate the normalized rolling count or sum on a
bounded write, matching the narrow raw-slot update.

## Invalid early-clock recovery

Read first copies the requested aggregate. The copy is returned unchanged when the firmware time
status is nonzero, the first time sample is greater than `946080000`, or average is zero. The last
case intentionally returns nonzero maximum/minimum bytes beside a zero average if that is what the
cache contains.

For a nonzero aggregate under an invalid early clock, the callback reproduces the stock signedness
defect: signed UTC-offset bits are interpreted as UInt16 and divided by 60. Thus `-300` minutes is
65,236/60, or 1,087 hours, which prevents every valid slot from reaching the queue. A usable
positive offset is subtracted from the slot index. A second time sample must be no earlier than the
first; otherwise the copied aggregate is redacted without enqueueing.

An eligible record is routed with local-day start zero, UTC offset zero, the first time sample as
its recorded timestamp, and the adjusted hour. The queue writer evaluates a third time sample.
These are three independent clock samples, not one value reused by the model. Whether the queue
accepts or rejects the record, the daily callback returns a zero aggregate. The result types expose
the disposition, unsigned offset, adjusted hour, and enqueue outcome without reading a live clock
or private SRAM.

## Clean implementation and provider boundary

`r1_health_u8_cache_reset`, `r1_health_u8_cache_write_slot`, and
`r1_health_u8_cache_read_slot` serve separate HR and SpO2 state/queue instances.
`r1_health_u16_cache_reset`, `r1_health_u16_cache_write_slot`, and
`r1_health_u16_cache_read_slot` preserve HRV's wider values. Tests cover reset-preserved latest
points, bounded writes, rolling-field preservation, valid status, strict cutoff comparison,
zero-average return, the negative-offset defect, backward validation time, queue-clock rejection,
adjusted-hour enqueue, retained FIFO bytes, zero day/offset metadata, and unconditional redaction.

The retained Nordic application exposes all six portable operations through its auditable health
API table. The UInt8 reset/write/read operations link at `0x00033104`, `0x00033134`, and
`0x00033B10`; the UInt16 operations link at `0x0003311C`, `0x00033158`, and `0x00033CC8`.
The table is at
`0x0003B274`, and the unsigned standalone image is 90,956 bytes text, 236 bytes
data, and 132,456 bytes BSS. Its HEX and BIN SHA-256 values are
`0954a9375874ee4f88139ba6243e20e1afba122e67afccba9d410e638053fa81` and
`31f3a97de9805239b03c51297f1de2ea9eaeff6fee372f1ea1f0c0a5c2f7bc91`.

Nordic SDK code continues to own the platform, scheduler, SoftDevice, and runtime
providers. Goodix and GoMore remain source-gated, FlashDB owns health database persistence, and no
live sensor, BLE command, private event publisher, flash mutation, signing bypass, or deployment
path is added by this slice.
