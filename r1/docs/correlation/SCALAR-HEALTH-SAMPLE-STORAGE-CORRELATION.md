# Scalar-health sample-storage correlation

## Outcome

OpenR1 now implements the product-owned heart-rate, SpO2, and HRV storage edge over values that an
external provider has already produced. It does not contain optical acquisition, filtering,
calibration, heart-rate/oxygen estimation, or GoMore logic. Those remain behind the Goodix and
GoMore licensed-provider boundaries.

The recovered event consumers, cache accessors, latest-point accessors, metadata refresh paths,
and aggregators are exact-size and SHA-256 pinned:

| Metric | Recovered extent | Bytes | Clean-room role |
| --- | --- | ---: | --- |
| HR | `0x0005ACE0..<0x0005ACE4` | 4 | daily-cache accessor |
| HR | `0x0005ACE8..<0x0005AD04` | 28 | latest-point accessor |
| HR | `0x0005AD08..<0x0005AD5C` | 84 | cache metadata refresh |
| HR | `0x0005AD90..<0x0005AE6C` | 220 | hourly storage aggregator |
| HR | `0x0008A80A..<0x0008A83E` | 52 | event consumer |
| HRV | `0x0005AF18..<0x0005AF1C` | 4 | daily-cache accessor |
| HRV | `0x0005AF20..<0x0005AF40` | 32 | latest-point accessor |
| HRV | `0x0005AF44..<0x0005AF5A` | 22 | cache metadata refresh |
| HRV | `0x0005AF60..<0x0005B042` | 226 | hourly storage aggregator |
| HRV | `0x0008A83E..<0x0008A866` | 40 | event consumer |
| SpO2 | `0x0005BAEC..<0x0005BAF0` | 4 | daily-cache accessor |
| SpO2 | `0x0005BAF4..<0x0005BB10` | 28 | latest-point accessor |
| SpO2 | `0x0005BB14..<0x0005BB28` | 20 | cache metadata refresh |
| SpO2 | `0x0005BB2C..<0x0005BC0C` | 224 | hourly storage aggregator |
| SpO2 | `0x0008A8AE..<0x0008A8D8` | 42 | event consumer |

The SpO2 aggregator and consumer are manual provenance supplements because Ghidra omitted their
function records. Their entry, complete return boundary, callers, neighboring functions, and exact
bytes are independently fixed by the analysis scripts and verifier. The other thirteen entries
come directly from the Ghidra function inventory.

## Metric contracts

Heart rate accepts the inclusive range `40...220`. A zero event timestamp is filled with the
caller-supplied firmware timestamp; a nonzero event timestamp is preserved. Rejected values do not
alter the cache or rolling accumulator. Accepted values request storage notification metric 0.

SpO2 accepts every UInt8 value with a minimum of 70; the recovered consumer has no additional
upper bound. It always replaces the event timestamp with firmware time, including when the event
already carried a nonzero timestamp. Accepted values request storage notification metric 1.

HRV accepts the complete UInt16 RMSSD domain, including zero. Like heart rate, it fills only a zero
timestamp and preserves a nonzero one. Accepted values request storage notification metric 5. A
zero RMSSD is stored and aggregated but the latest-point accessor reports it as unavailable,
matching the recovered zero-sentinel contract.

Thus the recovered storage-notification metric IDs 0, 1, and 5 map to heart rate, SpO2, and HRV.

All three aggregators make two independent local-hour observations. The first selects the daily
aggregate slot and the second selects the eight-byte rolling accumulator. The clean API receives
both hours explicitly so a time/offset transition between calls remains observable. UInt8 slots
contain average, maximum, and zero-sentinel minimum bytes; HRV slots contain the same fields as
UInt16 little-endian values. The rolling state is exactly eight logical bytes: hour, reserved,
UInt16 count, and UInt32 sum.

The shared lifecycle now includes exact body `0x0005AB6C..<0x0005AB9C` (48 bytes, SHA-256
`b74c5922f418626358ebc50a329da3a21491332e4a71f37d51177f8d79d7cc6c`) for snapshot and
`0x0005ACC4..<0x0005ACDC` (24 bytes, SHA-256
`6aa6b17190d13347fb6ac54f11b0efb3f95c1c059b6a7d83f047648e2bc61c44`) for restore.
`r1_health_accumulator_snapshot` zeroes both outputs unless a nonempty accumulator matches the
requested hour. `r1_health_accumulator_restore` ignores a zero count and otherwise updates
hour/count/sum while preserving the reserved byte. Caller-owned instances replace the stock
six-entry global array without collapsing metric separation.

## Clean implementation and safety corrections

`r1_heart_rate_store_sample`, `r1_spo2_store_sample`, and `r1_hrv_store_sample` implement only
range, timestamp, aggregation, compact-latest-point, and notification-routing policy.
`r1_health_u8_latest_sample` and `r1_health_u16_latest_sample` expose the recovered nonzero latest
value rule without private SRAM. The existing bounded daily-cache and offline-sync APIs complete
the storage lifecycle.

The stock shared average helper permits its UInt16 count to wrap to zero. In the HRV path that can
produce positive infinity or NaN before conversion back to an integer. OpenR1 returns
`R1_ERROR_CAPACITY` at `UINT16_MAX`, preserves the accumulator unchanged, and never divides by
zero. This changes only corrupt/saturated state; every normal reachable average remains identical.
Hour indexes are likewise restricted to `0...23`.

Tests cover both HR endpoints and rejections, the full SpO2 endpoint behavior, zero and nonzero
timestamp contracts, independent aggregate/average hours, all three notification metric IDs,
minimum/maximum/truncated averages, zero HRV storage with an unavailable latest point,
zero-sentinel recovery, output preservation on an unavailable latest point, invalid hours, and
counter saturation.

The retained Nordic application exports the scalar storage, accumulator, and latest-point APIs
through `.openr1_health_api`. The UInt8/UInt16 average helpers link at `0x00031F54` and
`0x00031FA4`; snapshot/restore at `0x00031FF4` and `0x00032016`; latest-point helpers at
`0x0003234C` and `0x00032376`; and HR, SpO2, and HRV stores at `0x000325C2`, `0x00032682`, and
`0x0003272E`. The retained table is at `0x0003B274` with size `0x110`. The verified unsigned image
is 94,804 bytes text, 236 bytes data, and 132,544 bytes BSS.
Its HEX and BIN SHA-256 values are
`48e1b3fadfdb956fbdf5f637d48c9a5808db5394848fb4538450c0ff98be80cf` and
`421a42cf37dad04dadcff5d3b1742efcba4ba50fd1d2e52f26bcf00e5df24d35`.

It contains no Goodix register or algorithm code, no GoMore code, no raw sensor access, no BLE
command path, no signing bypass, and no deployment operation.
