# Time and hourly health-rollover correlation

## Outcome

OpenR1 now implements the deterministic planning and synchronization-cursor portion of the
recovered clock-transition and local-hour pipeline. The implementation reports which external
provider actions are required; it does not publish private events, format a database, invoke a
GoMore binary, fabricate metric samples, or duplicate FlashDB allocation/TSDB code.

| Recovered extent | Size | Ownership boundary |
| --- | ---: | --- |
| `0x0005DC08..<0x0005DC5E` | 86 | R1 backward-clock adapter around the licensed GoMore provider |
| `0x0005DCE8..<0x0005DE98` | 432 | R1 hour/storage orchestrator around pinned FlashDB and six metric callbacks |
| `0x0005E698..<0x0005E956` | 702 | R1 time/storage orchestrator around pinned FlashDB, clock/calendar, and metric callbacks |

The Ghidra inventory contains the two storage orchestrators. The smaller GoMore callback was
omitted from that inventory; its stored callback pointer, complete prologue/control flow, provider
tail call, return at `0x0005DC5C`, and following data establish the exact 86-byte extent. All three
bodies are pinned by size and SHA-256. The GoMore function is classified only as a clean-room
adapter requiring a licensed provider. The two storage functions are classified as provider
adapters rather than standalone product algorithms because their original orchestration calls
FlashDB, allocation, time/calendar helpers, and metric callbacks.

## Material time transition

`r1_health_plan_time_transition` consumes the exact logical old/new tuple: signed UTC-offset
minutes and UInt32 Unix seconds. It always reports that the clock-update attempt occurs. Subscriber
broadcast is requested only when the offsets differ or absolute timestamp delta is at least 31
seconds; a 30-second same-zone correction therefore updates the clock without downstream fan-out.

For a broadcast transition:

- a backward jump of at least 180 seconds requests the external GoMore reinitialization adapter;
- a backward jump of at least 3,600 seconds requests destructive health-database formatting and a
  reset of the four known synchronization cursors;
- moving from a timestamp below `946080000` to that floor or above requests current-day recovery;
- a valid old timestamp whose old/new local-day quotients differ requests reset of all six daily
  aggregate cache families; and
- a valid old timestamp and new timestamp strictly above the floor run the known-cursor clamp pass.

The local-day comparison uses each side's own signed UTC offset. The result exposes old/new day
indexes and every requested side effect so the caller can bind admitted providers explicitly.
`health_database_format_requested` is information, not an exposed formatter or authorization to
erase storage.

## Exact hsync reconciliation

The recovered `hsync` record is six UInt32 words. Metric ownership is proven for offsets 0, 4, 12,
and 16 (HR, SpO2, HRV, and activity); offsets 8 and 20 remain unresolved.
`r1_health_sync_cursor_state` preserves that exact 24-byte layout.
`r1_health_reconcile_sync_cursors` resets or clamps only the four known fields and never modifies
the two unresolved words. A clamp replaces a cursor only when it is later than the new timestamp.
The result reports how many known words actually changed.

## Local-hour boundary

`r1_health_plan_hour_boundary` preserves the three-subscriber topology without implementing the
HRV or SpO2 providers. Both eligibility evaluations are requested for every event. The database
writer accepts only hours `0...23` and appends the previous hour (`0 -> 23`, otherwise `hour - 1`).
At hour zero it requests reset of all six daily cache families and attempts the slot-2 midnight
follow-up. Exhaustive registration evidence finds no slot-2 subscriber in this image, so the
result records the attempt and its no-op destination separately. An invalid hour such as 24 still
reaches the two eligibility subscribers but is rejected by the database writer.

## Clean implementation and provider use

The portable functions are pure and bounded. Tests cover the 30/31-second boundary, 180-second
GoMore threshold, 3,599/3,600-second database threshold, timezone-only day crossing,
invalid-to-valid recovery, strict floor behavior, reset/clamp of only four known cursor words,
unresolved-word preservation, midnight/1 a.m./invalid-hour mapping, six-cache reset count, and the
empty midnight subscriber slot.

The retained Nordic application exposes the three portable APIs through `.openr1_health_api`.
The transition planner, cursor reconciler, and hour planner link at `0x00031D54`, `0x00031E98`,
and `0x00031F06`; the table is at `0x0003B274`. The verified unsigned application is 90,956 bytes
text, 236 bytes data, and 132,456 bytes BSS. Its HEX and BIN SHA-256 values are
`0954a9375874ee4f88139ba6243e20e1afba122e67afccba9d410e638053fa81` and
`31f3a97de9805239b03c51297f1de2ea9eaeff6fee372f1ea1f0c0a5c2f7bc91`.
FlashDB 2.0.0/FAL remains the storage provider; the GoMore path remains disabled until its exact
licensed SDK is authenticated. No internal-event sender, live clock setter, private SRAM reader,
database formatter, BLE command, signing bypass, or deployment mechanism is added.
