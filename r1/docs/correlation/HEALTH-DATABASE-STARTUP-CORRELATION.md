# Health database startup correlation

## Outcome

The recovered application function at `0x00070030..<0x0007023E` is a
product-owned health-database startup orchestrator. Its 526-byte body has
SHA-256 `67cf421c59889f89122546e1bfc3b349b163d78a2b679c398144f13c9fec55db`.
It coordinates attributable FlashDB, RTOS allocation/mutex, and blocked
time/calendar providers with the already admitted health crash-record lifecycle;
it does not implement any of those providers.

OpenR1 implements the R1-specific ordering and policy in `r1_health_db_startup`.
The linked Nordic image continues to compile pinned FlashDB 2.0.0 with bundled
FAL 0.5.99 and authenticated FreeRTOS-Kernel 10.5.1. Database, mutex, allocation, time,
calendar, and iteration operations remain explicit provider callbacks so this
controller does not recreate upstream or unidentified code.

The adjacent four-byte entry at `0x00070028..<0x0007002C` is the database
singleton accessor. Its exact bytes are `00 48 70 47` and its SHA-256 is
`06936d0536d64e86c623270163a043c1b484bbc978af8fbf56cd1650cbfb6587`.
Five recovered public health-history synchronizers call it before their
FlashDB queries. OpenR1 represents only that R1 binding seam with
`r1_health_db_provider_handle`; the caller injects the actual provider-owned
database object.

## Exact recovered sequence

The stock body performs these operations in order:

1. Add byte 1 from each of six 16-byte schema descriptors. Continue only when
   `(schema_sum + 8) < 129`, which admits at most 120 schema bytes in the
   128-byte record.
2. Call FlashDB `fdb_tsdb_control` with control values 2 and 3, corresponding to
   `FDB_TSDB_CTRL_SET_LOCK` and `FDB_TSDB_CTRL_SET_UNLOCK`.
3. Call pinned FlashDB `fdb_tsdb_init` with database name `health`, partition
   name `health.db`, a provider time callback, and maximum record length 128.
   The exact strings are present at `0x00070268` and `0x0007025C` in the stock
   image. A nonzero FlashDB result terminates startup.
4. Ensure the database mutex exists, then subscribe time-listener
   channels 1 followed by 0.
5. If the retained record has its magic and a valid nonzero crash timestamp,
   set provider timestamp and UTC offset. Mark the provider clock valid only
   when the retained validity bit is set. Clear the retained time fields and
   reseal the record CRC.
6. Read the current UTC timestamp and signed UTC offset. Convert to local
   calendar form, clear hour/minute/second while preserving the calendar
   provider's upper state byte, then convert back to the UTC timestamp for the
   start of the local day.
7. Allocate 128 bytes. On success, zero the workspace, run
   `fdb_tsl_iter_by_time(database, local_day_start, now, recovery_callback,
   workspace)`, release the workspace, and invoke the admitted one-shot crash
   snapshot restore. On allocation failure, skip both database recovery and
   crash snapshot restore.

Logging branches are diagnostic only and are not part of the behavioral API.
The clean-room result structure makes the stock void function's observable
terminal cases explicit without changing normal sequencing.

## Provider and ownership boundary

| Recovered dependency | Ownership treatment | OpenR1 boundary |
| --- | --- | --- |
| `0x00063694` / `fdb_tsdb_control` | pinned FlashDB 2.0.0 | injected control callback; exact values 2 then 3 |
| `0x00063814` / `fdb_tsdb_init` | pinned FlashDB 2.0.0 | injected initializer with exact names and 128-byte limit |
| `0x00063AD8` / `fdb_tsl_iter_by_time` | pinned FlashDB 2.0.0 | injected recovery iterator callback |
| CMSIS mutex and FreeRTOS allocation/free | Nordic SDK and authenticated CMSIS-FreeRTOS providers | injected ensure/allocate/release operations |
| `0x0008AF8C` listener registry | unresolved generic event-provider seam | injected subscription callback; channels 1 then 0 |
| `0x0008ADA4...0x0008AF40` time/calendar calls | blocked time/calendar provider | injected clock and local-day-start callbacks |
| `0x00058960`, `0x000589E8`, `0x00058A24`, `0x00059EE4` | admitted R1 crash-record behavior | typed OpenR1 APIs called directly |

No Goodix, GoMore, GXCAS, QMA6100, YHM2710, IQS7211E, ST25DVxxKC, motion,
optical, temperature-acquisition, or health-algorithm body is admitted by this
closure. The time/calendar implementation remains blocked; only its call
contract is represented.

## Verification

Tests pin the 120-byte accepted and 121-byte rejected schema sums, provider-free
rejection, explicit singleton provider binding, controls 2 then 3, fatal initialization failure, listener order 1
then 0, separate set-clock and conditional mark-valid calls, retained-time
clear with valid CRC, current-clock/day-start propagation, allocation failure,
zeroed 128-byte recovery workspace, exact recovery interval, release ordering,
and one-shot crash snapshot restore. Strict C11, ASAN/UBSAN, and freestanding
Cortex-M4 builds pass.

The ownership verifier pins both stock extents, lengths, hashes, and their
bounded product/FlashDB dispositions. The linked controller is 464 bytes at
`0x00039E90` with SHA-256
`8292ead8e375fa260a6acfdb549e427612388db620572c8f974f0cf4883adaeb`.
The linked provider-handle accessor is at `0x00039E8C`. The `.openr1_health_db_api` retention table is at `0x00045BD0` with size `0x08`.
The verified unsigned Nordic application is 126,028 bytes text, 276 bytes data,
and 148,956 bytes BSS. Its standalone HEX and BIN SHA-256 values are
`cc082ebf2ed4105a20f4bf1feda7708e8ed2a9a97cea28559cf089d86e109d2d`
and `d1b36e3e70e65f1b0847a3a6587813297b2cd782f25ea6bf6cffc723c6d9046c`.

This component changes no signing, boot verification, rollback, authorization,
flash-protection, or deployment behavior.
