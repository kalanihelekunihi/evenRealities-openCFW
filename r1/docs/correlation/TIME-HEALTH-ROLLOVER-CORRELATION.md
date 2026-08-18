# Time and hourly health-rollover correlation

## Outcome

OpenR1 implements the deterministic planning and synchronization-cursor portion of the
recovered clock-transition and local-hour pipeline. The exact GoMore backward-clock adapter now
compiles as a typed callback seam, and its tail action resolves to the already transparent provider
reset routine. The portable implementation reports or dispatches caller-bound actions; it does not publish private events,
format a database, fabricate metric samples, or duplicate FlashDB
allocation/TSDB code.
The source-built Zephyr composition separately binds the admitted slot-1 hour event and
non-destructive FlashDB append route described below.

| Recovered extent | Size | Ownership boundary |
| --- | ---: | --- |
| `0x0005DC08..<0x0005DC5E` | 86 | owner-authorized R1 backward-clock adapter into the transparent GoMore reset path |
| `0x0005DCE8..<0x0005DE98` | 432 | R1 hour/storage orchestrator around pinned FlashDB and six metric callbacks |
| `0x0005E698..<0x0005E956` | 702 | R1 time/storage orchestrator around pinned FlashDB, clock/calendar, and metric callbacks |

The Ghidra inventory contains the two storage orchestrators. The smaller GoMore callback was
omitted from that inventory; its stored callback pointer, complete prologue/control flow, provider
tail call, return at `0x0005DC5C`, and following data establish the exact 86-byte extent. All three
bodies are pinned by size and SHA-256. The GoMore adapter body SHA-256 is
`fc72eda6d9921b4c09e94214ac0d1b66bc3afdfa40fbdda80a213e76e1999d85`; its terminal branch at
`0x0005DC58` targets the transparent `gomore_primitives_reset_provider_state` reconstruction of
`0x0004C37C`. The two storage functions are classified as provider
adapters rather than standalone product algorithms because their original orchestration calls
FlashDB, allocation, time/calendar helpers, and metric callbacks.

## Material time transition

`r1_health_plan_time_transition` consumes the exact logical old/new tuple: signed UTC-offset
minutes and UInt32 Unix seconds. It always reports that the clock-update attempt occurs. Subscriber
broadcast is requested only when the offsets differ or absolute timestamp delta is at least 31
seconds; a 30-second same-zone correction therefore updates the clock without downstream fan-out.

For a broadcast transition:

- a backward jump of at least 180 seconds dispatches or requests the GoMore reinitialization adapter;
- a backward jump of at least 3,600 seconds requests destructive health-database formatting and a
  reset of the four known synchronization cursors;
- moving from a timestamp below `946080000` to that floor or above requests current-day recovery;
- a valid old timestamp whose old/new local-day quotients differ requests reset of all six daily
  aggregate cache families; and
- a valid old timestamp and new timestamp strictly above the floor run the known-cursor clamp pass.

`r1_gomore_time_transition_adapter` mirrors the callback itself: NULL input returns without action;
it loads the old/new UInt32 timestamps at logical offsets 4 and 8, rejects forward/equal time, and
uses unsigned subtraction for the inclusive 180-second threshold. The UTC-offset words are ignored.
On acceptance it invokes a caller-bound reset action exactly once. Passing no action is an explicit
planning-only safety extension and still returns the exact decision.

The local-day comparison uses each side's own signed UTC offset. The result exposes old/new day
indexes and every requested side effect so the caller can bind admitted providers explicitly.
`health_database_format_requested` is information, not an exposed formatter or authorization to
erase storage.

## Exact hsync reconciliation

The recovered `hsync` record is six UInt32LE words. Metric ownership is proven for offsets 0, 4,
12, and 16 (HR, SpO2, HRV, and activity); offsets 8 and 20 remain unresolved.
`r1_health_sync_cursor_state` preserves that exact 24-byte layout, and the strict portable
decode/encode APIs round-trip all six words without native-layout dependence.
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

The portable functions are bounded. Tests cover NULL input/action, forward/equal time, 179/180-second
adapter boundaries, unsigned maximum rewind, single callback dispatch, the 30/31-second boundary, 180-second
GoMore threshold, 3,599/3,600-second database threshold, timezone-only day crossing,
invalid-to-valid recovery, strict floor behavior, reset/clamp of only four known cursor words,
unresolved-word preservation, midnight/1 a.m./invalid-hour mapping, six-cache reset count, and the
empty midnight subscriber slot.

The retained Nordic application exposes the three portable APIs through `.openr1_health_api`.
The transition planner, cursor reconciler, and hour planner link at `0x00031D54`, `0x00031E98`,
and `0x00031F06`; the table is at `0x0003B274`. The verified unsigned application is 94,804 bytes
text, 236 bytes data, and 132,544 bytes BSS. Its HEX and BIN SHA-256 values are
`48e1b3fadfdb956fbdf5f637d48c9a5808db5394848fb4538450c0ff98be80cf` and
`421a42cf37dad04dadcff5d3b1742efcba4ba50fd1d2e52f26bcf00e5df24d35`.
FlashDB 2.0.0/FAL remains the storage provider. The retained Nordic application does not compose
the live GoMore graph. The separate source-built Zephyr target now owns typed engine state,
initialization, all 16 recovered stages, input topics, result routing, and fresh-engine reset; its
physical inputs and output equivalence still require owned-hardware validation. No private SRAM reader,
database formatter, BLE command, signing bypass, or deployment mechanism is added.

## Source-built Zephyr composition

The Zephyr clock worker samples the valid local hour at the recovered 1,024-tick cadence,
suppresses the first valid observation, and multicasts slot 1 only when the hour changes.
The health listener serializes the previous hour from the six live/module-owned cache families
with `r1_health_db_build_record`, encodes the exact 128-byte body, and calls pinned FlashDB
`fdb_tsl_append`. At midnight the append attempt precedes all six cache resets and the empty
slot-2 multicast. Append failures remain observable counters.

This source binding does not invent samples: activity, HR, SpO2, and HRV reflect only existing
runtime caches; temperature changes only after the dormant exact one-shot producer completes;
stress remains zero until a producer is bound. Slot 0 now receives the exact little-endian
12-byte tuple (old offset, new offset,
old timestamp, new timestamp). An invalid-to-valid transition reruns the bounded current-day
FlashDB iterator, and a valid local-day change resets all six caches to the new day metadata.
Day-start conversion and workspace failures are counted and skip recovery rather than widening
the iterator interval.
The clock suppresses a local-hour append for the same material correction by establishing a
new baseline after slot-0 delivery.

The Zephyr composition loads this exact record from the fixed 24-byte `hsync` class during
`kv.bin` startup. Reset or effective clamp actions re-encode it and commit through the hardened
snapshot writer; the two unresolved words remain unchanged. REG1 and hsync writers share one
mutex, and successful cursor commits and failures have separate counters.

The source binding does not expose the stock error-3 database format-and-retry branch or execute a
live GoMore reset. Slot 0 does call `r1_gomore_time_transition_adapter`; its bound action records the
existing suppressed-action counter, preserving the exact adapter call seam without inventing engine
state. Executing the reset still requires validated engine composition, while destructive formatting
requires a separate owned-hardware recovery decision.
