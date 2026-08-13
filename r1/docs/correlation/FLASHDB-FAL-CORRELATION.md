# FlashDB and FAL provider correlation

## Decision

The R1 application links upstream FlashDB **2.0.0**, commit
`4e5677408256f82d47cd56a6b04605dcee35ed9a`, together with the FAL **0.5.99** snapshot nested in
that release. openR1 therefore consumes those authenticated sources for `health.db`; it does not
reconstruct their implementations from decompiler output. Local source is limited to the R1 flash
device port, the recovered seven-entry partition table, and product policy around the database.

This supersedes the earlier 1.1.1/0.5.0 candidate. The older source reproduces basic `TSL0`
geometry, but it cannot reproduce the recovered release-specific control flow.

## Release discrimination

Two independent features coexist at tag 2.0.0 and in the R1 binary:

- `_fdb_db_path` at `0x0003F014` returns the FAL partition name when file mode is disabled. Its
  recovered callers and structure offsets match `src/fdb.c`.
- `fdb_tsl_iter_by_time` at `0x00063AD8` selects reverse sector and TSL traversal when `from > to`.
  The recovered indirect targets include `get_last_sector_addr` at `0x0006A158` and
  `get_last_tsl_addr` at `0x0006A176`; its range tests and binary search match `src/fdb_tsdb.c`.

The compiled FAL initializer at `0x00062F40` embeds `0.5.99`, independently confirming the nested
FAL snapshot. Vendor verification checks the release markers and SHA-256 hashes of every linked
FlashDB/FAL translation unit. The host storage test additionally requires 26 records to be returned
in descending timestamp order, so an older forward-only implementation cannot pass.

## FlashDB function map

These 33 recovered function entries are complete upstream bodies and are source-routed to
FlashDB 2.0.0:

| Address | Upstream symbol | Address | Upstream symbol |
| --- | --- | --- | --- |
| `0x0003F014` | `_fdb_db_path` | `0x0003F022` | `_fdb_flash_erase` |
| `0x0003F03E` | `_fdb_flash_read` | `0x0003F05A` | `_fdb_flash_write` |
| `0x0003F076` | `_fdb_get_status` | `0x0003F094` | `_fdb_init_ex` |
| `0x0003F2EC` | `_fdb_init_finish` | `0x0003F384` | `_fdb_set_status` |
| `0x0003F3B0` | `_fdb_write_status` | `0x00057EB4` | `check_sec_hdr_cb` |
| `0x0006366C` | `fdb_blob_make` | `0x00063672` | `fdb_blob_read` |
| `0x00063694` | `fdb_tsdb_control` | `0x00063814` | `fdb_tsdb_init` |
| `0x00063A28` | `fdb_tsl_append` | `0x00063AB8` | `fdb_tsl_clean` |
| `0x00063AD8` | `fdb_tsl_iter_by_time` | `0x00063CB4` | `fdb_tsl_query_count` |
| `0x00063D40` | `fdb_tsl_to_blob` | `0x000650C4` | `format_all_cb` |
| `0x000650D4` | `format_sector` | `0x0006A158` | `get_last_sector_addr` |
| `0x0006A176` | `get_last_tsl_addr` | `0x0006A194` | `get_next_sector_addr` |
| `0x0006A1B2` | `get_next_tsl_addr` | `0x00087428` | `query_count_cb` |
| `0x00087C24` | `read_sector_info` | `0x00087E14` | `read_tsl` |
| `0x000895F4` | `sector_iterator` | `0x00093744` | `tsl_append` |
| `0x00093828` | `tsl_format_all` | `0x00094AE0` | `update_sec_status` |
| `0x0009763C` | `write_tsl` |  |  |

The decompiler did not emit standalone function-inventory rows for reverse helpers
`0x0006A158`/`0x0006A176` or `query_count_cb` at `0x00087428`. Their complete bodies have proven
indirect-target or callback boundaries and are admitted as byte-pinned manual supplements rather
than inferred from a nearest address. `write_tsl` lies inside the broad
FreeRTOS address interval but has the exact FlashDB two-phase record write sequence and is called
by `tsl_append`; it is explicitly excluded from the FreeRTOS cluster.

## FAL function map

These ten entries match the FAL 0.5.99 snapshot bundled by FlashDB 2.0.0:

| Address | Upstream symbol | Ownership effect |
| --- | --- | --- |
| `0x00057E1C` | `check_and_update_part_cache` | provider cache/table validation |
| `0x00062DF4` | `fal_flash_device_find` | provider device lookup |
| `0x00062E68` | `fal_flash_init` | provider device initialization |
| `0x00062F40` | `fal_init` | provider top-level initialization |
| `0x00062FF4` | `fal_partition_erase` | provider partition operation |
| `0x00063150` | `fal_partition_find` | provider partition lookup |
| `0x000631C0` | `fal_partition_init` | provider table initialization |
| `0x000631E8` | `fal_partition_read` | provider partition operation |
| `0x00063358` | `fal_partition_write` | provider partition operation |
| `0x00064F74` | `flash_device_find_by_part` | provider partition-cache helper |

The locally compiled `r1_fal_port.c` implements only the provider-neutral callbacks and recovered
partition configuration required by `fal_cfg.h`; none of the functions above is locally recreated.
The Nordic target binds those callbacks to the recovered 36-page **internal** flash region through
Nordic `nrf_fstorage_sd`. See
[`INTERNAL-FLASH-CORRELATION.md`](INTERNAL-FLASH-CORRELATION.md).

## Integrity and licensing

The pin is reproducible from the commit archive whose SHA-256 is
`7758fb46976acebc754fb452bbac2144badc713a3e158bab8a8961bc112eca1b`. The manifest also pins
individual hashes for `fdb.c`, `fdb_tsdb.c`, `fdb_utils.c`, `fal.c`, `fal_flash.c`, and
`fal_partition.c`.

FlashDB's top-level source is Apache-2.0. The nested FAL snapshot's license file and linked source
headers also identify Apache-2.0. Distribution must preserve the applicable notices; the license
does not change the source-ownership rule that identifiable FAL code is consumed upstream.
