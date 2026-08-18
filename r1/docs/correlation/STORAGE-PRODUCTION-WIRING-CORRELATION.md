# Storage production-wiring correlation

## Scope

How the three recovered R1 databases — the `kv.bin` four-snapshot class store, the
FlashDB-provided `health.db` TSDB, and the R1-owned `sleep.db` circular journal — are
initialized in the Nordic production image. Format/ownership evidence for each store is
pinned separately in [`KV-STORE-CORRELATION.md`](KV-STORE-CORRELATION.md),
[`FLASHDB-FAL-CORRELATION.md`](FLASHDB-FAL-CORRELATION.md),
[`HEALTH-DATABASE-STARTUP-CORRELATION.md`](HEALTH-DATABASE-STARTUP-CORRELATION.md),
[`INTERNAL-FLASH-CORRELATION.md`](INTERNAL-FLASH-CORRELATION.md), and
[`VALIDATED-SLEEP-DELIVERY-CORRELATION.md`](VALIDATED-SLEEP-DELIVERY-CORRELATION.md);
this record covers only the production startup binding added on top of them.

## Stock evidence

- The kv.bin partition bind (`0x00094E3C`), class registration (`0x000731A0`), and startup
  sector scrub (`0x00057D0C`) belong to the device-initialization chain; the portable
  `r1_kv_store_initialize` only reads flash, so it may run on the SoftDevice event thread
  in the same relative position.
- The stock storage startup task at `0x000926DC` calls the health-database startup
  orchestrator (`0x00070030`) first and the sleep.db FAL bind thunk (`0x0008DD8C` →
  `0x0005B0F8`) later in the same body. The bind passes the partition-name string at
  `0x0005B18C`, evidence-pinned as `"sleep.db"`, to `fal_partition_find` (`0x00063150`).
- The health startup reads the six 16-byte schema descriptors at `0x00099BF4`; byte 1 of
  each is `{3, 3, 3, 3, 24, 6}` (sum 42, +8 overhead < 129), and initializes FlashDB with
  the exact strings `"health"` (`0x00070268`) and `"health.db"` (`0x0007025C`), a provider
  time callback (`0x0006A230`), and a 128-byte record limit.
- `openr1_storage.c` rejects flash mutations from the SoftDevice event thread because the
  `nrf_fstorage_sd` completion callback is dispatched by that thread's
  `nrf_sdh_evts_poll()`; `fdb_tsdb_init` may format an empty `health.db` partition, so the
  health/sleep startup must run on a separate worker.

The complete Ghidra-omitted task entry is now byte-pinned as
`0x000926DC..<0x000927BA` (222 bytes, SHA-256
`b13c5bc01f09f51f5b4dc9a79566d9b5dcaff74cdf6e8447b12e3d8affa8a179`). Beyond the
health-before-sleep ordering, it creates a 50-record queue of 16-byte event records, runs ten
startup actions in the recovered order, signals task group 7, registers the name `"service"`
with a 10,000-tick watchdog interval, and waits on the low 24 thread-flag bits. Bit 22 drains and
dispatches queued event records; bit 23 signals suspension and enters the recovered indefinite
wait. Queue creation failure enters the stock fail-stop boundary.

`r1_service_task_plan_startup` and `r1_service_task_plan_flags` preserve this deterministic
orchestration as typed actions. They do not create a queue, manipulate interrupt priority, enter
an infinite loop, or invoke any database/cache/provider body. Those effects remain in CMSIS-
FreeRTOS and the separately source-gated product/provider functions named by the action list.

## OpenR1 wiring

New glue: `r1/platform/nrf52840/sdk/openr1_databases.c` / `openr1_databases.h`, called from
`main.c` immediately after `openr1_clock_initialize()` (the health ops adopt and report
time through the platform clock) and after `openr1_storage_initialize()` (the FAL table
must exist).

Startup order:

1. `openr1_databases_initialize` (SoftDevice event thread): verifies the `kv.bin` FAL
   partition (offset 0, two pages) and runs `r1_kv_store_initialize` synchronously —
   read-only, fail-explicit on any read/validation error. Loads the persisted REG1 flag
   (kv dev_info byte 24 bit 1), resets the platform private event bus, creates the health
   database CMSIS mutex, then starts the `storage` worker thread.
2. `storage` worker: runs `r1_health_db_startup` with the recovered schema bytes and ops
   bound to production providers (below), then binds `sleep.db` through
   `fal_partition_find("sleep.db")` + `r1_sleep_db_initialize` at the partition offset.
   This preserves the recovered health-before-sleep ordering. The worker then stays
   resident and applies deferred REG1 persist requests (`openr1_databases_persist_reg1`)
   so writers on the SoftDevice event thread never mutate flash directly.

The portable startup plan additionally retains the full stock action order: hardware-resource
initialization; health database; heart-rate, SpO2, temperature, stress, and activity cache
metadata refresh; sleep database; HRV cache refresh; and protocol-port state reset. The production
ports may bind only the actions for which they own typed runtime state; omitted live actions remain
explicit rather than being silently fabricated.

Health startup op bindings:

| Op | Production binding |
| --- | --- |
| `control` (2 then 3) | `fdb_tsdb_control` `FDB_TSDB_CTRL_SET_LOCK` / `SET_UNLOCK` registering CMSIS-mutex lock/unlock wrappers |
| `initialize` | pinned FlashDB `fdb_tsdb_init(&tsdb, "health", "health.db", get_time, 128, NULL)`; the SDK image now compiles `fdb.c`, `fdb_tsdb.c`, and `fdb_utils.c` (it previously linked FAL only) |
| `get_time` (FlashDB callback) | `openr1_clock_epoch`; fail closed — an unsynchronized clock (`r1_clock_now` reports false) yields timestamp 0 and never a fabricated time |
| `ensure_mutex` | idempotent CMSIS mutex creation (the mutex is created eagerly during `openr1_databases_initialize`) |
| `subscribe_time` | bound to the platform `r1_event_bus` instance: the recovered channels 1 then 0 are bus slots 1 (local-hour boundary) and 0 (wall-clock/timezone transition), subscribed fail-explicitly with a delivery-recording listener; the recovered listener bodies are not part of the admitted closure. The bus queue sink is now bound (update 2026-08-14): `openr1_event_bus.c` creates one CMSIS queue per event-id window plus a consumer thread that delivers records through `r1_event_bus_multicast` same-context (see [`EVENT-BUS-CORRELATION.md`](EVENT-BUS-CORRELATION.md)); a bind failure leaves the sink unbound and `r1_event_bus_publish` returns `R1_ERROR_UNSUPPORTED` |
| `set_clock` | `openr1_clock_adopt_phone_time` (crash-time handoff) |
| `mark_clock_valid` | no-op: adoption validates the offset and marks the clock synchronized atomically; `r1_clock` has no separate validity flag |
| `current_clock` | `openr1_clock_epoch` plus the new `openr1_clock_utc_offset` getter; fail closed as 0/0 when unsynchronized |
| `local_day_start` | shift to local, convert through the owner-authorized reconstructed `time_calendar_unix_to_broken_down`, subtract hour/minute/second, then shift back to UTC; the hardware RTC/backend remains unbound |
| `allocate` / `release` | FreeRTOS `pvPortMalloc` / `vPortFree` (heap_4) |
| `recover` | `fdb_tsl_iter_by_time` over the recovered `[local_day_start, now]` interval with the controller's zeroed 128-byte workspace; each record is bounds-read into that workspace and counted. Decoding bodies into the RAM caches remains a separate health-storage consumer and is not fabricated here |

The crash record lives in the `.openr1_noinit` `NOLOAD` section so the recovered
crash-time handoff and one-shot snapshot restore survive a watchdog or software reset;
the activity/HR/SpO2/HRV RAM caches are static zero-initialized state owned by this
module until their consumers land.

## Failure and power-loss policy

Initialization is fail-explicit: any failure sets a sticky first-error word
(`openr1_databases_last_error`), the health startup result is retained
(`openr1_databases_health_startup`), and the affected database stays unbound — its
accessor returns NULL rather than a partial object. No recovery path erases or rewrites
existing state: the stock "format everything" recovery is not reproduced, the kv store
keeps its hardened block-7 commit record and alternating-sector rollover (block 0
programmed last as the visibility marker), and the sleep journal keeps its
body-before-header commit. See [`../SECURITY.md`](../SECURITY.md).

## Alternate Zephyr source binding (2026-08-16)

The source-built `openr1_nrf52840` target now consumes the same authenticated
FlashDB 2.0.0/FAL 0.5.99 sources rather than substituting a Zephyr-native TSDB.
Its CMake boundary requires the pinned root and compiles `fdb.c`, `fdb_tsdb.c`,
`fdb_utils.c`, `fal.c`, `fal_flash.c`, and `fal_partition.c` together with the
existing R1 `fdb_cfg.h`, `fal_cfg.h`, and `r1_fal_port.c`. The package gate
checks the archive pin, every consumed header/license/source hash, and a
nonempty loadable linker-map span for all six provider objects.

Zephyr initializes the source wall clock first, binds the recovered `0x24000`-
byte flash window to FAL, requires the seven-entry table and exact `health.db`
offset/length (`0x2000`/`0x6000`), then performs health startup before the
portable `sleep.db` bind. FlashDB's 32-bit write granularity is preserved over
the serialized flash-map adapter; no alternate journal format is introduced.
The startup callbacks use a Zephyr mutex and heap, the source clock and
reconstructed exact calendar day-start adapter, a no-init 966-byte crash record, and R1 event-bus
slots 1 then 0. Crash restoration targets the live runtime activity, heart-rate,
SpO2, and HRV histories. The recovered standalone HR averaging accumulator has
no runtime field and therefore remains explicit module-owned state.

The iterator performs a bounded decode/restore pass over the recovered local-day
interval. It requires exactly 128 bytes, preserves the reserved word and 78-byte
tail, decodes the signed offset/recorded-timestamp metadata and exact metric
widths, and derives both the prior local hour (hour 23 at midnight) and its
local-day start from those body fields. The TSL timestamp remains the bounded
query/index key. Six activity words are unpacked as 12/10/10-bit fields; a zero word
remains an invalid/empty bucket. Matching cache writers restore activity, HR,
SpO2, and HRV without fabricating sample counts, sums, latest measurements, or
temperature/stress runtime fields. Separate visited, decoded, restored, and
rejected counters make short or invalid-time records observable without making
startup destructive.

The same Zephyr composition now binds the non-destructive hourly production
route. After suppressing the first valid local-hour observation, the source clock
multicasts each actual hour change on slot 1. The subscribed health listener builds
the exact zero-initialized 128-byte body from the previous activity/HR/SpO2/
temperature/stress/HRV cache slot, writes the current recorded UTC timestamp and
signed offset, and appends through `fdb_tsl_append`. At hour zero it performs the
append attempt before resetting all six caches, then attempts the recovered empty
slot-2 follow-up. Temperature and stress are explicit module-owned zero histories
until typed producers are bound. This route never generates biometric samples.

Append failures are counted rather than invoking the stock error-3 whole-database
format-and-retry branch. Slot 0 now decodes the exact 12-byte old/new signed-offset
and timestamp tuple and applies the admitted branches: an invalid-to-valid transition
runs the same bounded current-day iterator, while a valid local-day change resets all
six caches to the new day metadata. Invalid day-start conversion or workspace allocation
increments a recovery-failure counter and never widens the query to timestamp zero.
The fixed `hsync` class is decoded as six UInt32LE words at startup. Reset/clamp actions
persist only the four named cursors through the hardened `kv.bin` snapshot writer while
preserving both unresolved words; commit success/failure is observable. Destructive formatting
remains suppressed. Backward-clock GoMore reinitialization is live and its success/failure is
counted separately.
Retail-data migration, power-loss testing, and physical validation remain separate gates.

## Tests and gates

The portable formats and the startup controller remain covered by `test_openr1.c` and
`test_vendor_storage.c`. The Nordic glue is verified by its linked-image build; the Zephyr
glue is verified by a clean sysbuild, source-boundary gate, final linker-map inspection,
artifact signature check, and bundle source lock. Owned-ring validation — real partition
contents, migration, power-loss behavior, SoftDevice/Zephyr radio coexistence, and clock-sync
interaction — remains an explicit hardware gate.
