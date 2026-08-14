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

Health startup op bindings:

| Op | Production binding |
| --- | --- |
| `control` (2 then 3) | `fdb_tsdb_control` `FDB_TSDB_CTRL_SET_LOCK` / `SET_UNLOCK` registering CMSIS-mutex lock/unlock wrappers |
| `initialize` | pinned FlashDB `fdb_tsdb_init(&tsdb, "health", "health.db", get_time, 128, NULL)`; the SDK image now compiles `fdb.c`, `fdb_tsdb.c`, and `fdb_utils.c` (it previously linked FAL only) |
| `get_time` (FlashDB callback) | `openr1_clock_epoch`; fail closed — an unsynchronized clock (`r1_clock_now` reports false) yields timestamp 0 and never a fabricated time |
| `ensure_mutex` | idempotent CMSIS mutex creation (the mutex is created eagerly during `openr1_databases_initialize`) |
| `subscribe_time` | bound to the platform `r1_event_bus` instance: the recovered channels 1 then 0 are bus slots 1 (local-hour boundary) and 0 (wall-clock/timezone transition), subscribed fail-explicitly with a delivery-recording listener; the recovered listener bodies are not part of the admitted closure, and the bus queue sink stays deliberately unbound (the stock per-window RTOS queue send plus consumer dispatcher is more than trivial glue), so `r1_event_bus_publish` returns `R1_ERROR_UNSUPPORTED` on this instance |
| `set_clock` | `openr1_clock_adopt_phone_time` (crash-time handoff) |
| `mark_clock_valid` | no-op: adoption validates the offset and marks the clock synchronized atomically; `r1_clock` has no separate validity flag |
| `current_clock` | `openr1_clock_epoch` plus the new `openr1_clock_utc_offset` getter; fail closed as 0/0 when unsynchronized |
| `local_day_start` | toolchain-`gmtime_r` adapter (shift to local, clear hour/minute/second, shift back to UTC) per the route decision in [`../boundaries/TIME-CALENDAR-PROVIDER-BOUNDARY.md`](../boundaries/TIME-CALENDAR-PROVIDER-BOUNDARY.md); no code from the blocked time/calendar family |
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

## Tests and gates

The portable formats and the startup controller remain covered by `test_openr1.c` and
`test_vendor_storage.c`; the new glue is platform-only (it needs the Nordic SDK, CMSIS,
and FlashDB) and is verified by the linked-image build, which must compile and link
`openr1_databases.c`, `fdb.c`, `fdb_tsdb.c`, and `fdb_utils.c` cleanly. No portable code
was added, so no host tests changed; the gmtime day-start adapter is exercised on target
only. Owned-ring validation — real partition contents, migration, power-loss behavior,
SoftDevice queue coexistence, and clock-sync interaction — remains an explicit hardware
gate.
