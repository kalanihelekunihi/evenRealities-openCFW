# Health-history routing correlation

## Outcome

OpenR1 now has a bounded, typed model of the production health registration lookup and internal
history-request routing. It reproduces the public HR, SpO2, HRV, activity, and sleep daily/point
membership while deliberately omitting an internal-event sender. Temperature and stress remain
absent from the phone-history route even though they have separate local caches.

The exact recovered bodies are SHA-256 pinned:

| Recovered extent | Bytes | Role |
| --- | ---: | --- |
| `0x00082BE8..<0x00082C0C` | 36 | health registration dispatcher |
| `0x00083298..<0x000832D2` | 58 | 14-entry binary search |
| `0x00082C10..<0x00082C44` | 52 | activity refresh handler |
| `0x00082C44..<0x00082C8A` | 70 | activity daily handler |
| `0x00082C8A..<0x00082CCE` | 68 | HR daily handler |
| `0x00082CCE..<0x00082D14` | 70 | HRV daily handler |
| `0x00082D14..<0x00082D5A` | 70 | sleep daily handler |
| `0x00082D5A..<0x00082D9E` | 68 | SpO2 daily handler |
| `0x00082E34..<0x00082E66` | 50 | HR point handler |
| `0x00082E66..<0x00082E9A` | 52 | HRV point handler |
| `0x00082E9A..<0x00082ECE` | 52 | SpO2 point handler |
| `0x00083930..<0x00083972` | 66 | HR point response wrapper |
| `0x00083972..<0x000839B4` | 66 | HRV point response wrapper |
| `0x0008B8E8..<0x0008BA80` | 408 | event-14 history consumer |

Ten handler extents are manual inventory supplements because Ghidra did not emit function rows for
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

The two point-response wrappers are also product-routed and exact-hash pinned. They select an empty
typed result when no point exists and otherwise pass the recovered 8-byte HR or 9-byte HRV payload
through the public transport abstraction. Their SHA-256 values are
`e8525e642988dccd5218353948d9b90e269a42698ff6f0a049c94dd5bea50b35` and
`5be0afbd7a6296c529e0df91825c13c8fb1645af137828d82eafdbad04a16741`.

Tests cover all nine event-producing registrations, exact metrics, kinds, serials, residues,
round-trip event encoding, five registered non-event/no-op handlers, a missing temperature-family
key, temperature/stress rejection, exact-length enforcement, and the existing public daily wire
path. OpenR1 does not expose an internal-event sender, report-enable control, test injector, raw
provider operation, signing bypass, or deployment operation.

The route, encoder, and decoder link at `0x000327DC`, `0x0003284C`, and `0x00032874`. The retained
`.openr1_health_api` table is at `0x0003B274` with size `0x110`. The verified unsigned application
is 90,956 bytes text, 236 bytes data, and 132,456 bytes BSS. Its HEX and BIN SHA-256 values are
`0954a9375874ee4f88139ba6243e20e1afba122e67afccba9d410e638053fa81` and
`31f3a97de9805239b03c51297f1de2ea9eaeff6fee372f1ea1f0c0a5c2f7bc91`.
