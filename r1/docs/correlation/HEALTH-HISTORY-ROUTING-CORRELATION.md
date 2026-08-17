# Health-history routing correlation

## Outcome

OpenR1 now has a bounded, typed model of the production health registration lookup and internal
history-request routing. It reproduces the public HR, SpO2, HRV, activity, and sleep daily/point
membership while deliberately omitting an internal-event sender. Temperature and stress remain
absent from the phone-history route even though they have separate local caches.

The exact recovered bodies are SHA-256 pinned:

| Recovered extent | Bytes | Role |
| --- | ---: | --- |
| `0x0004286E..<0x0004287C` | 14 | event-14 non-null/exact-length gate |
| `0x00082BE8..<0x00082C0C` | 36 | health registration dispatcher |
| `0x00083298..<0x000832D2` | 58 | 14-entry binary search |
| `0x00082C10..<0x00082C44` | 52 | activity refresh handler |
| `0x00082C44..<0x00082C8A` | 70 | activity daily handler |
| `0x00082C8A..<0x00082CCE` | 68 | HR daily handler |
| `0x00082CCE..<0x00082D14` | 70 | HRV daily handler |
| `0x00082D14..<0x00082D5A` | 70 | sleep daily handler |
| `0x00082D5A..<0x00082D9E` | 68 | SpO2 daily handler |
| `0x00082D9E..<0x00082DBE` | 32 | sleep-detail private-event plan |
| `0x00082DBE..<0x00082DF8` | 58 | HR measurement plan |
| `0x00082DF8..<0x00082DFA` | 2 | registered no-op callback; SHA-256 `c7dfbb7d02759eacb64dbc916c1bb6f21eabaff1c1032ea5c9176abf7fd28df8` |
| `0x00082DFA..<0x00082E34` | 58 | SpO2 measurement plan |
| `0x00082E34..<0x00082E66` | 50 | HR point handler |
| `0x00082E66..<0x00082E9A` | 52 | HRV point handler |
| `0x00082E9A..<0x00082ECE` | 52 | SpO2 point handler |
| `0x00082ECE..<0x00082EE8` | 26 | report-setting selector |
| `0x00083930..<0x00083972` | 66 | HR point response wrapper |
| `0x00083972..<0x000839B4` | 66 | HRV point response wrapper |
| `0x0008B8E8..<0x0008BA80` | 408 | event-14 history consumer |

Fifteen handler extents are manual inventory supplements because Ghidra did not emit function rows for
them; their adjacent entries, complete bodies, return boundaries, table pointers, and hashes are
independently fixed. The dispatcher and event consumer were already product-routed. The binary
search is newly admitted from its exact table-local semantics rather than presumed vendor code.

## Registration and event contract

The 14 sorted keys are `0101`, `0102`, `0103`, `0201`, `0202`, `0203`, `0401`, `0402`, `0403`,
`0501`, `0502`, `0601`, `0602`, and `7f01`. The successful stock search leaves deterministic
lower-bound residue values `0/1/0/3/3/5/0/7/7/9/7/11/11/13` in a volatile register. Nine handlers
copy that inert residue into an event-14 record; it is not caller context or an authorization
token.

The record is exactly eight bytes:

| Offset | Field |
| ---: | --- |
| 0 | metric UInt8 |
| 1 | query kind UInt8: point/refresh 0, daily 1 |
| 2...3 | request serial UInt16LE |
| 4...7 | dispatcher residue UInt32LE |

The recovered consumer validates the full length but reads only offsets 0...3. OpenR1 preserves
and exposes the residue for forensic equivalence, then ignores it for routing as production does.
The clean decoder accepts HR metric 0, SpO2 1, activity 4, HRV 5, and sleep-daily metric 6. It
rejects temperature 2, stress 3, sleep point, unknown metrics, unknown kinds, and non-eight-byte
records.

This independently confirms that temperature and stress are not public history routes.

The four remaining non-event handlers are now modeled separately. Sleep detail (`0602`) requests
private event `100e`. HR and SpO2 measurement (`0103` and `0203`) request provider mode 2 with the
incoming serial, then request one-byte value `1` on private events `1002` and `1004`. All three
require request flag bit 1 and reject flag bit 0. The `7f01` handler canonicalizes its optional
payload byte into a report-setting boolean; the clean no-payload path produces false directly
instead of reproducing the stock read from address zero. These are pure plans only: no private
event publication, provider invocation, or report/test-state mutation is exposed.

Daily handlers request an immediate empty response before asynchronous history delivery. HR,
SpO2, and HRV point handlers return their compact current point. Activity `0502` is a refresh-only
route with no direct response. Daily HR, SpO2, activity, and HRV backfill engines share the
recovered flash limit of 259,200 seconds (three days); persistence and transport remain separate
providers.

## Clean implementation and safety

`r1_health_history_route_command`, `r1_health_history_encode_event14`, and
`r1_health_history_decode_event14` implement the pure lookup/record boundary. `r1_dispatch` uses
the route result while retaining its stronger authenticated-session gate and direct typed output
path. The point routes now use the recovered nonzero latest-value accessors, including zero-HRV
unavailability.

`r1_sleep_detail_plan`, `r1_heart_rate_measurement_plan`,
`r1_spo2_measurement_plan`, and `r1_health_report_setting_plan` reproduce the four auxiliary
command decisions. `r1_health_history_noop_handler` represents the exact standalone `bx lr`
callback at `0x00082DF8`. It intentionally has no provider, storage, transport, or state
dependency.

`r1_health_history_event_valid` reproduces the exact event-14 consumer gate: the record pointer
must be non-null and its length must be exactly eight bytes. It does not publish or consume an
internal event; accepted caller-owned bytes still pass through the typed decoder above.

The two point-response wrappers are also product-routed and exact-hash pinned. They select an empty
typed result when no point exists and otherwise pass the recovered 8-byte HR or 9-byte HRV payload
through the public transport abstraction. Their SHA-256 values are
`e8525e642988dccd5218353948d9b90e269a42698ff6f0a049c94dd5bea50b35` and
`5be0afbd7a6296c529e0df91825c13c8fb1645af137828d82eafdbad04a16741`.

Tests cover all nine event-producing registrations, exact metrics, kinds, serials, residues,
round-trip event encoding, auxiliary flag acceptance/rejection, exact measurement commands and
private events, canonical report-setting values, all five registered non-event/no-op handlers, a
missing temperature-family key, temperature/stress rejection, exact-length enforcement, and the
existing public daily wire path. OpenR1 does not expose an internal-event sender, report-enable
control, test injector, raw provider operation, signing bypass, or deployment operation.

The route, encoder, and decoder link at `0x000327DC`, `0x0003284C`, and `0x00032874`. The retained
`.openr1_health_api` table is at `0x0003B274` with size `0x110`. The verified unsigned application
is 94,804 bytes text, 236 bytes data, and 132,544 bytes BSS. Its HEX and BIN SHA-256 values are
`48e1b3fadfdb956fbdf5f637d48c9a5808db5394848fb4538450c0ff98be80cf` and
`421a42cf37dad04dadcff5d3b1742efcba4ba50fd1d2e52f26bcf00e5df24d35`.
