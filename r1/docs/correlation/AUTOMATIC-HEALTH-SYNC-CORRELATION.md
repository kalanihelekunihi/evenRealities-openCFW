# Automatic health-sync correlation

## Outcome

Application `2.2.6.0009` contains an R1-owned orchestration path that automatically publishes the
five public health-history families while an authenticated phone is connected. This path is
separate from the GoMore sleep/health algorithm and Goodix optical-algorithm providers: it reads
already-produced R1 history and routes it through the public synchronization functions. openR1
therefore implements only the observed scheduling and dispatch policy, while provider-gated
algorithms and hardware acquisition remain outside this boundary.

## Recovered function boundary

| Recovered extent | Size | Clean evidence name | Observed role |
| --- | ---: | --- | --- |
| `0x0004CBB0..<0x0004CBC4` | 20 | `r1_authenticated_phone_connection_gate` | tests whether the authenticated phone link exists |
| `0x0008B138..<0x0008B180` | 72 | `r1_automatic_health_sync_gate` | applies the shared three-hour gate and calls the five legs |
| `0x0008B818..<0x0008B82E` | 22 | `r1_unsynchronized_sleep_batch_sync` | emits eligible unsynchronized sleep records |
| `0x0008BAEC..<0x0008BE3C` | 848 | `r1_activity_history_sync` | emits activity history |
| `0x0008C150..<0x0008C49A` | 842 | `r1_heart_rate_history_sync` | emits heart-rate history |
| `0x0008C750..<0x0008CA9C` | 844 | `r1_hrv_history_sync` | emits HRV history |
| `0x0008CD60..<0x0008D0AC` | 844 | `r1_spo2_history_sync` | emits blood-oxygen history |

All seven extents come directly from the Ghidra function inventory and are byte-pinned by the
project verifier. They are recorded as `r1_product_specific` / `clean_room_behavior_only`; this
classification does not claim original authorship, and it does not admit any vendor algorithm.

## Exact observable policy

The common gate behaves as follows:

1. If the authenticated phone connection gate is false, it does nothing and does not change the
   timestamp.
2. It starts a batch when the shared timestamp is zero, when the current clock is less than the
   stored timestamp, or when at least `10,800` seconds have elapsed.
3. An elapsed value of `10,799` seconds does not start a batch; exactly `10,800` does.
4. It calls the legs in this order: heart rate (`0x0008C150`), SpO2 (`0x0008CD60`), HRV
   (`0x0008C750`), activity (`0x0008BAEC`), then unsynchronized sleep (`0x0008B818`).
5. Each automatic leg uses serial identifier zero.
6. After the calls, it writes the current time to the shared timestamp without aggregating a
   success result from the legs.
7. The explicit history-query consumer at `0x0008B8E8` resets that same timestamp before routing
   the selected query, so a phone query restarts the automatic cooldown.

The recovered health-report enable flag is not consulted by this gate. Temperature and stress are
not automatic batch legs. These details are independently captured in the first-party
`R1AutomaticHealthSyncEvidence` executable model and its tests.

## Clean implementation

`r1_health_run_automatic_sync` owns the portable gate, exact leg order, serial-zero behavior, clock
rewind handling, and timestamp update. `r1_health_note_explicit_history_query` implements the
shared query timestamp rule. `r1_runtime_run_automatic_health_sync` derives the phone-connected
condition from an encrypted, bonded, authorized `R1_ROLE_PHONE` link and delegates to the portable
controller. Existing
typed health encoders, output queues, acknowledgement tracking, and storage adapters remain the
only data paths; no generic registry or raw vendor transport was added.

Both product targets now call the controller from their admitted once-per-second wall-clock
cadence. `r1_runtime_schedule_automatic_health_sync` records the exact five-leg order in a bounded
bitset, and `r1_runtime_service_automatic_health_sync` admits one leg only after the recovered
50-record shared BLE queue drains. This matters at the exact boundary: sixteen maximum-size sleep
sessions plus their response require 49 fragments, while a worst-case scalar history query can
produce 29 models. The Nordic CMSIS queue publishes an explicit idle predicate; Zephyr uses the
portable event-plane count. Disconnecting the phone discards an unfinished batch. Host tests
cover the disconnected, authentication, initial, cooldown, exact boundary, clock-rewind,
explicit-query, call-order, serial-zero, drain-aware five-leg service, and shared cooldown
timestamp cases.
The Nordic `.openr1_health_api` retention table remains as a linker-auditable view of the same
controller even though its live caller is now composed.

## Security and provider limits

Automatic publication does not relax authorization. A live batch requires the runtime's phone
role gate, and explicit history requests still pass the existing encrypted, bonded, authorized
dispatcher checks. This work does not reconstruct GoMore or Goodix code, does not add a raw
biometric interface, and does not alter signing, boot verification, rollback, ACL, APPROTECT, or
deployment enforcement.
