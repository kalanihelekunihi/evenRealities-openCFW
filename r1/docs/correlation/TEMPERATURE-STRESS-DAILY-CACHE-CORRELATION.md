# Temperature and stress daily-cache correlation

## Outcome

OpenR1 implements the product-owned storage edge for temperature and stress. The source-built
Zephyr target binds the reconstructed GXCAS GXT310 register transport, exact raw conversion,
two-address probe, bounded paired acquisition/calibration path, exact `"temp"` stream, and dormant
one-shot listener. When explicitly started, that listener composes the recovered five-sample
reducer and event 9 consumer into the temperature daily cache. It does not assign physical channel
roles or clinical units. Stress generation and mode control remain behind the
transparent-but-uncomposed GoMore boundary. The two product-owned stress-control event consumers
are now represented as pure action plans, but they do not invoke that boundary. The portable
storage code replaces accepted values'
timestamps with firmware time, maintains hourly aggregates, and serves the recovered daily-cache
callbacks.

The recovered bodies are exact-size and SHA-256 pinned:

| Recovered extent | Bytes | Clean-room role |
| --- | ---: | --- |
| `0x000422C8..<0x00042318` | 80 | one-byte stress-mode event consumer |
| `0x00042474..<0x000424CA` | 86 | one-byte stress-measurement event consumer |
| `0x0005ABA0..<0x0005AC38` | 152 | shared six-instance UInt8 hourly-average accumulator |
| `0x0005BCCC..<0x0005BCD0` | 4 | stress cache accessor |
| `0x0005BCD4..<0x0005BCE8` | 20 | stress cache day/offset refresh |
| `0x0005BCEC..<0x0005BDC8` | 220 | stress storage aggregation |
| `0x0005BE5C..<0x0005BE60` | 4 | temperature cache accessor |
| `0x0005BE64..<0x0005BE78` | 20 | temperature cache day/offset refresh |
| `0x0005BE7C..<0x0005BF74` | 248 | temperature storage aggregation |
| `0x0008A8D8..<0x0008A8FC` | 36 | bounded stress event consumer |
| `0x0008A8FC..<0x0008A928` | 44 | bounded temperature event consumer |
| `0x00091124..<0x0009113E` | 26 | stress daily reset |
| `0x0009113E..<0x00091158` | 26 | stress daily read |
| `0x00091158..<0x00091172` | 26 | stress daily write |
| `0x000918DE..<0x000918F8` | 26 | temperature daily reset |
| `0x00091918..<0x00091950` | 56 | temperature early-clock read/redaction |
| `0x00091954..<0x0009196E` | 26 | temperature daily write |

Seven extents omitted by Ghidra's function inventory are manual provenance supplements with
unambiguous prologue, return, caller, and adjacent-data boundaries. The verifier hashes the exact
bytes for all seventeen entries. The shared accumulator is product bookkeeping rather than a signal
algorithm: it selects one of six logical metric instances, resets on a new local hour or zero
count, increments a UInt16 count and UInt32 sum, and returns the truncated positive average.

## Temperature representation and cache behavior

The temperature event consumer accepts the inclusive published range `250...500`. These are
already-produced temperature values; OpenR1 does not claim or recreate how either sensor derives
them. Storage uses an exact one-byte offset equal to published minus 250, so the admitted range maps
to `0...250`. Values outside the range are ignored before clock or local-hour access. Accepted
events replace the event timestamp with firmware time and store a compact latest point containing
the offset and replacement timestamp.

Aggregation calls the local-hour path twice. The first hour selects the three-byte daily slot; the
second selects/resets the independent eight-byte rolling accumulator. OpenR1 exposes both as typed
inputs so the recovered mismatch behavior remains testable. The returned rolling average replaces
the slot average, while maximum and zero-sentinel minimum are updated from the current offset.

Temperature reset clears 24 aggregate triples and updates signed UTC offset and local-day start,
while preserving the compact latest-point region. Read first copies one triple. It returns that
copy when time status is valid, the sampled timestamp is strictly greater than `946080000`, or the
copied average is zero. Otherwise it redacts all three bytes. There is no temperature offline FIFO,
acknowledgement callback, or standalone phone-history route in this image.

## Stress representation and cache behavior

Internal system event `0x1007` reaches `0x000422C8`. The consumer accepts exactly one byte and
forwards its unsigned value to the stock mode setter. That setter changes state only for values
zero and one, so `r1_stress_mode_control_plan` preserves an accepted-but-no-update result for
`2...255`. Internal event `0x1008` reaches `0x00042474`; it also requires exactly one byte and
canonicalizes zero to disabled and every nonzero value to enabled before the provider-facing tail
call. `r1_stress_measurement_control_plan` records that Boolean intent without making the call.
Wrong-length events are inert. Neither plan publishes a private event, starts a timer, accesses
sensor state, or creates a public BLE command.

The stress event consumer accepts `0...100`; a value above 100 is ignored before sampling time or
local hour. Accepted values use the same separate aggregate-hour and average-hour calls, update the
same three-byte aggregate shape, and retain a compact latest point. Zero is a valid stored sample,
including the recovered all-zero first aggregate.

Stress daily reset and write share the bounded UInt8 cache operations. Stress read is a plain
three-byte copy: it does not sample the clock, redact early data, enqueue offline data, or update an
acknowledgement cursor. The recovered stress cache address aliases a separately observed HRV
accumulator address in the stock SRAM map. OpenR1 does not reproduce that private alias; each clean
state object is caller-owned, eliminating accidental cross-metric memory coupling.

## Clean implementation and safety boundary

`r1_health_u8_accumulate_average`, `r1_temperature_store_sample`,
`r1_stress_store_sample`, `r1_stress_mode_control_plan`,
`r1_stress_measurement_control_plan`, `r1_temperature_cache_read_slot`, and
`r1_stress_cache_read_slot` implement the behavior over typed state. Existing bounded UInt8 reset
and write operations serve both caches. The accumulator rejects the stock wrap-to-zero division
fault at `UINT16_MAX`; cache indexes are restricted to `0...23` even though the stock callbacks do
not check them.

The source-built one-shot composition and its exact listener/callback/state evidence are documented
separately in `TEMPERATURE-ONE-SHOT-CORRELATION.md`. No listener starts at boot and no public BLE
measurement route is inferred.

Tests cover both range endpoints and rejections, published-to-offset conversion, replacement
timestamps, distinct aggregate/average hours, average/minimum/maximum updates, zero stress and
temperature offsets, reset-preserved latest points, valid/plausible/early clocks, zero-average
return, plain stress reads, invalid indexes, and accumulator saturation.

The retained Nordic application exposes these five portable APIs through `.openr1_health_api`.
The average helper, temperature store, stress store, temperature read, and stress read link at
`0x00031F54`, `0x00032902`, `0x000329B4`, `0x0003317C`, and `0x000331EC`. The retained table is at
`0x0003B274`. The verified unsigned application is 94,804 bytes text, 236 bytes data, and 132,544 bytes BSS. Its HEX and BIN SHA-256 values are
`48e1b3fadfdb956fbdf5f637d48c9a5808db5394848fb4538450c0ff98be80cf` and
`421a42cf37dad04dadcff5d3b1742efcba4ba50fd1d2e52f26bcf00e5df24d35`.
This portable cache component adds no GXT310 register constants or transport, no GoMore stress
algorithm, no raw sensor or private SRAM access, no internal-event injection, no BLE command, no
signing bypass, and no deployment path. The separate Zephyr GXT310 adapter owns those exact
register constants and transport while keeping production cache injection absent.
