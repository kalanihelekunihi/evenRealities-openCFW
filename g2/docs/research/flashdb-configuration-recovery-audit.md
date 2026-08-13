# FlashDB 2.1.1 configuration and FAL ABI recovery audit

Status: production-excluded research recovery. No overlay, manifest, release
pin, firmware artifact, or hardware state changed. The fail-closed, read-only
analyzer `tools/analyze_g2_flashdb.py` authenticates the official G2
`2.2.6.10` Apollo-main image and is guarded by
`tests/test_analyze_g2_flashdb.py`.

All addresses below are run addresses under
`run = file_offset + 0x00437FE0`.

## Result

The three previously open compile-time parameters are now closed by static
recovery:

| Parameter | G2 value | Independent evidence |
|---|---:|---|
| `FDB_WRITE_GRAN` | `1` bit | The `read_kv` body `[0x00544000,0x0054418E)` uses the 24-byte v2.1.1 KV header unique to the 1-bit layout; the compiled `norflash` FAL record independently stores `write_gran = 1` at `+0x34` |
| `sec_size` | `0x1000` (4096 bytes) | Neither database caller issues control command 0; `_fdb_init_ex` therefore copies the compiled device `blk_size = 0x1000` from `fal_flash_dev + 0x20` |
| `FDB_KV_CACHE_TABLE_SIZE` | `64` | `fdb_kvdb_init` has an exact 64-iteration, 8-byte-stride loop writing `kv_cache_table[i].addr` at object offset `0xAC` |

The same initializer independently recovers
`FDB_SECTOR_CACHE_TABLE_SIZE = 64`: its first 64-iteration loop uses a
24-byte stride and writes the short-enum `kvdb_sec_info` fields at
`+0x2A8/+0x2AC/+0x2BC`.

This tranche closes the two default-table descriptors and all 21 default
values. Twenty reside in initialized SRAM; reset's independently authenticated
zero scatter supplies the `kvbooCount` word. It also recovers the database
mutex callbacks, exact NOR callback return conventions, eleven record-migration
callbacks, and first-party magic/reset policy. These are static facts, not
permission to run the destructive policy on hardware.

## Identity and feature set

- FlashDB version literal `2.1.1`: `0x0078D60C`.
- Stock `_fdb_init_finish` banner: `0x00754944`.
- `[FlashDB][kv]` and `[FlashDB][utils]` are present.
- `[FlashDB][tsdb]`, `.tsl`, and `tsdb` are absent, proving that no live or
  retained TSDB subsystem exists in the authenticated image. This does not
  prove the original `FDB_USING_TSDB` preprocessor state because linker
  garbage collection could have discarded a compiled TSDB translation unit.
- `__ver_num__` and its update diagnostic are absent, proving
  `FDB_KV_AUTO_UPDATE` is off.
- Stock debug-only strings such as `KVDB size is` and `The oldest addr is`
  are absent, proving `FDB_DEBUG_ENABLE` is off.
- FAL mode is live; file mode is not compiled into the recovered control
  path.

The stock bodies pinned by the analyzer are:

| Upstream function | Stock range | Bytes | SHA-256 |
|---|---|---:|---|
| Even `sysenv` initializer wrapper | `[0x004D96D8,0x004D9A84)` | 940 | `9fa5ed5c2df612cdd46667b4f9f4a536f884c44484c65c629ba20becb238190a` |
| Even `factory` initializer wrapper | `[0x0051079C,0x00510992)` | 502 | `34674ed6155198d4ae3db6e87ecf98fa5039a7709970867f74a4c9b5b0424957` |
| `read_kv` | `[0x00544000,0x0054418E)` | 398 | `1afc3c8acc4d095995d504e4c6b7ae68c0face093fe5c0c23b0a6299a8863c28` |
| `fdb_kvdb_init` | `[0x005453FE,0x0054552C)` | 302 | `c40571f5f8710c17ca10a713ec7dd6fa7a32da2fac0e2c1571806ff33cd03aad` |
| Even database-object accessor | `[0x00541232,0x00541240)` | 14 | `a6ce82abb413ebb05e36f957ec398e3503a2d9fa7eea371b40fe09e2d052d40d` |
| FAL partition read wrapper | `[0x00597D34,0x00597D72)` | 62 | `bd8aef1675f28c9b51abfd974f1bc7d3ed9cf3d64a0dba974f6d2ad9876d6c50` |
| FAL partition write wrapper | `[0x00597D72,0x00597DB0)` | 62 | `2f1b6688f627b068ba062edf1b985c268ba805a803b1b51b003c6a3d693510dd` |
| FAL partition erase wrapper | `[0x00597DB0,0x00597DEA)` | 58 | `9f34d5139292961ffe7f117181feddf1fe51c686c43f3feea855ca21abde6047` |

## Corrected database bindings

Focused call-site recovery corrects earlier prose that treated adjacent
strings as database names:

| Static object | Database name passed as `name` | FAL partition passed as `path` |
|---:|---|---|
| 0 | `sysenv` | `kvdb` |
| 1 | `factory` | `NVdb` |

The analyzer checks the actual literal-pool edges, not just adjacent strings:
`0x004D9AD4 -> 0x0078E594` (`sysenv`),
`0x004D9AB8 -> 0x0078E58C` (`kvdb`),
`0x005109D0 -> 0x0078E60C` (`factory`), and
`0x005109D4 -> 0x0078E614` (`NVdb`). The complete containing initializer
wrappers above are independently SHA-256 pinned.

The bytes `01PEkvdb` at `0x006D5358` are the little-endian FAL magic
`0x45503130` (`01PE`) immediately followed by the first partition name. They
are not one combined FlashDB database name.

Both callers set only `FDB_KVDB_CTRL_SET_LOCK` (command 2) and
`FDB_KVDB_CTRL_SET_UNLOCK` (command 3), at
`0x004D9744/0x004D9752` and `0x005107C2/0x005107D0`. No sector-size override
is present in either initializer.

## Default KV tables from authenticated initialized SRAM

The official image's fail-closed IAR initialized-data record at `0x0075D3F0`
decodes 17,752 bytes to `0x20000000..0x20004557` (SHA-256
`df1a1fdf7b2792a7c4ef7a2c5cc6d1423bc7833b556fdfcedb8d6d927fbbb743`).
That range contains the actual 12-byte `fdb_default_kv_node` arrays, not just
nearby strings. Each node is `{key pointer, value pointer, explicit
value_len}`. Therefore every entry is an explicit-length FlashDB blob;
FlashDB stores no application C type or per-node callback in this ABI. Any
more specific struct interpretation remains first-party schema work.

`sysenv` uses 12 nodes at `0x2000372C`:

| Key | Bytes | Initialized default (hex) |
|---|---:|---|
| `kvString` | 9 | `6b76537472696e6700` |
| `kvMagic` | 4 | `2000005a` (`0x5A000020`, little-endian) |
| `kvbooCount` | 4 | `00000000`; `0x20074988` lies in authenticated startup-zero range `[0x20004558,0x20075048)` |
| `kvTime` | 12 | `010000002b2d376820000000` |
| `kvTimeFormat` | 12 | `010000000000000000000000` |
| `kvTemperatureUnit` | 12 | `010000000000000000000000` |
| `kvUniversalSetting` | 20 | `030000000100000000000000ffffffffffff0000` |
| `kvSetting` | 28 | `0164010000000000060101001e000000000000000000000000000000` |
| `kvOnboardingConfig` | 1 | `00` |
| `kvRing` | 24 | `01ffffffffffff4556454e2052315f464646464646000000` |
| `kvTerminalMode` | 4 | `01000000` |
| `kvAlsScale` | 12 | `010000000004000000000000` |

`factory` uses nine nodes at `0x20003868`:

| Key | Bytes | Initialized-default evidence |
|---|---:|---|
| `nvString` | 9 | `6e76537472696e6700` |
| `nvMagic` | 4 | `22005555` (`0x55550022`, little-endian) |
| `nvProdMode` | 4 | `01000000` |
| `nvSysDt` | 172 | full bytes emitted by analyzer JSON; SHA-256 `f2b3d283ef574404c0d9c402a52a43cba58c0d415f23d7d6d8f38005aca7f05d` |
| `nvAdvMagic` | 4 | `01200000` |
| `nvMAC` | 10 | `01000000000000000000` |
| `nvSCald` | 92 | full bytes emitted by analyzer JSON |
| `nvSCaldAG` | 68 | full bytes emitted by analyzer JSON |
| `nvBuzzer` | 12 | `02000000a00f00001e000000` |

The complete descriptor functions, table-consuming validators, IAR records,
decoded output hashes, keys, pointers, lengths, and initialized bytes are all
mutation tested. `kvbooCount` is not inferred from its address. Reset calls the
authenticated zero-scatter path, whose record at `[0x0075D3C8,0x0075D3E0)`
selects the 56-byte zero handler at `0x005FA01E` and clears
`[0x20004558,0x20075048)`. The count word is wholly inside that range. The
closed `service_kvdb.c` initializer then reads the persisted word, increments
it, writes it back, and runs eleven separately closed record-migration
callbacks. All 21 default values and the boot-counter lifecycle are therefore
statically authenticated.

## Locking callbacks

Both databases install the same callbacks: Thumb entry `0x005410DB` for lock
and `0x00541127` for unlock. They operate on the single CMSIS mutex object at
`0x20074944`. Initialization at `[0x00541088,0x005410DA)` creates that mutex;
lock `[0x005410DA,0x00541126)` calls the CMSIS acquire seam at `0x004497B6`
with wait value `0xFFFFFFFF` (forever), and unlock
`[0x00541126,0x0054116E)` calls release at `0x0044981C`. Failures are logged,
but the `void` FlashDB callback ABI cannot propagate them. There are no
per-key callbacks in `fdb_default_kv_node`.

## FAL partition table and flash device

The compiled table begins at `0x006D5358`, contains two 64-byte
`fal_partition` records, and uses magic `0x45503130`:

| Partition | Device | Offset | Length |
|---|---|---:|---:|
| `kvdb` | `norflash` | `0x01FC0000` | `0x00038000` (224 KiB) |
| `NVdb` | `norflash` | `0x01FF8000` | `0x00008000` (32 KiB) |

The single compiled `fal_flash_dev` at `0x00722B30` is:

| Field | Value |
|---|---:|
| name | `norflash` |
| `addr` | `0x01FC0000` |
| `len` | `0x02000000` |
| `blk_size` | `0x00001000` |
| `ops.init` | `0x00540ED1` (Thumb) |
| `ops.read` | `0x00540ED5` (Thumb) |
| `ops.write` | `0x00540F2D` (Thumb) |
| `ops.erase` | `0x00540F85` (Thumb) |
| `write_gran` | `1` bit |

The FAL partition wrappers at `0x00597D34`, `0x00597D72`, and
`0x00597DB0` bounds-check `offset + size` against `fal_partition.len` at
`+0x38`, add `fal_partition.offset` at `+0x34`, resolve the device named at
partition `+0x1C`, and dispatch through device callbacks `+0x28/+0x2C/+0x30`.
Earlier notes calling `+0x34/+0x38` `fdb_db` fields were incorrect; those
offsets belong to the 64-byte FAL partition record.

The exact Even device callbacks are now recovered too:

| Callback | Body | Underlying MX25 seam | Return convention |
|---|---|---|---|
| init | `[0x00540ED0,0x00540ED4)` | none | always 0 |
| read | `[0x00540ED4,0x00540F2C)` | `0x004709C8` | requested byte count if driver returns 0; otherwise 0 |
| write | `[0x00540F2C,0x00540F84)` | `0x004708A8` | requested byte count if driver returns 0; otherwise 0 |
| erase | `[0x00540F84,0x00541088)` | `0x0047075C` | requires 4-KiB-aligned start, rounds size up, erases sector-by-sector, returns 4096 after total success; otherwise 0 |

This exposes an important first-party error-mapping defect/compatibility
constraint. The compiled FlashDB low-level adapters at
`[0x00585A12,0x00585A72)` and upstream 2.1.1 consider only a *negative* FAL
return an error. The Even callbacks return zero, not negative, on device
failure. Thus the stock path can report `FDB_NO_ERR` after a transport
failure. A source-owned port must return `-1` on failure and must not preserve
this unsafe behavior merely for byte-level compatibility.

## First-party format/reset policy

The complete wrappers prove a simple policy rather than a versioned
migration:

- `sysenv` reads `kvMagic` and requires `0x5A000020`;
- `factory` reads `nvMagic` and requires `0x55550022`;
- a missing or mismatched magic calls upstream `fdb_kv_set_default` for that
  database, erasing its sectors and recreating all defaults;
- the only direct first-party reset calls are `0x004D990E` and `0x0051093C`;
  `0x005452CC` is the stock corruption fallback inside FlashDB load; and
- `FDB_KV_AUTO_UPDATE` is absent, so there is no upstream per-version or
  per-key migration path. G2 instead invokes eleven first-party record
  callbacks after the boot-count update.

Consequently the recovered behavior is a wholesale destructive reset, not a
schema migration. The meaning and lifecycle of the first-party structures,
factory calibration records, and `kvbooCount` remain outside upstream
FlashDB and should stay in openCFW-owned policy code.

## Database object ABI

The Even accessor at `0x00541232` returns
`0x2005DFFC + index * 0x8AC`. There are two adjacent static `fdb_kvdb`
objects. The recovered ABI requires 32-bit pointers/`size_t` and short enums:

| `fdb_db` field | Offset |
|---|---:|
| `name` | `0x00` |
| `type` | `0x04` |
| `storage.part` | `0x08` |
| `sec_size` | `0x0C` |
| `max_size` | `0x10` |
| `oldest_addr` | `0x14` |
| `init_ok`, `file_mode`, `not_formatable` | `0x18`, `0x19`, `0x1A` |
| `lock`, `unlock`, `user_data` | `0x1C`, `0x20`, `0x24` |

Within `fdb_kvdb`, the KV cache starts at `0xA8`, the sector cache at
`0x2A8`, and the final `user_data` pointer at `0x8A8`. The total stride is
`0x8AC`. This layout proves short enums: `kvdb_sec_info` is 24 bytes; the
default 32-bit-enum ABI would be 32 bytes and cannot produce the stock loop.
Production compilation must therefore enforce the equivalent of
`-fshort-enums` and add compile-time `sizeof`/`offsetof` assertions.

Because `FDB_KV_AUTO_UPDATE` is absent, no `ver_num` field exists. Because the
callers do not set `not_formatable`, stock format-on-init-failure behavior is
reachable. That path must not be enabled in source firmware until a disposable
copy has passed corruption and power-loss tests.

## Exact vendored upstream source closure

Primary-source inspection of the official
`https://github.com/armink/FlashDB.git` tag `2.1.1` establishes:

- `refs/tags/2.1.1` is a lightweight tag;
- commit `714d6159e7e6afb267a3953756abca445c350e61`;
- tree `3410ae8111e4dbf6ae22d995bfcf37274abf89ea`;
- parent `f0af0eeda4d43732c620451ef6b5fff4e31dfc82`;
- commit payload size 1122 and SHA-256
  `c8aa69a97bdbaebdc283abd3e46fb025270654e4104de7b5caf9981528122ee5`;
- Apache-2.0 license.

The production-excluded snapshot in `third_party/flashdb` contains exactly
this smallest official KVDB/FAL closure:

1. `LICENSE`
2. `inc/fdb_cfg.h` (reference template only; do not use as the G2 config)
3. `inc/fdb_def.h`
4. `inc/fdb_low_lvl.h`
5. `inc/flashdb.h`
6. `src/fdb.c`
7. `src/fdb_kvdb.c`
8. `src/fdb_utils.c`
9. `port/fal/LICENSE`
10. `port/fal/inc/fal.h`
11. `port/fal/inc/fal_def.h`
12. `port/fal/src/fal.c`
13. `port/fal/src/fal_flash.c`
14. `port/fal/src/fal_partition.c`

Do not vendor/link `fdb_tsdb.c`, `fdb_file.c`, `fal_rtt.c`, shell code, demos,
or sample device ports for the recovered G2 build.
`third_party/flashdb/verify_snapshot.py` fails closed on the signed commit
object behind the lightweight tag and seven authenticated tree entry lists.
It reconstructs each canonical Git tree payload and proves the complete
commit -> tree -> path -> blob chain for all 14 selected files, then checks
per-file Git mode/blob ID/SHA-256, the exact file set, official-image hash,
compiled FAL records, and recovered configuration header. `make
vendor-snapshots` runs it offline. The snapshot has no production
registration.

The source-owned G2 configuration should express exactly:

```c
#define FDB_USING_KVDB
#define FDB_USING_FAL_MODE
#define FDB_WRITE_GRAN 1
#define FDB_KV_CACHE_TABLE_SIZE 64
#define FDB_SECTOR_CACHE_TABLE_SIZE 64
```

The recovered minimal config leaves `FDB_USING_TSDB` undefined because no
live/retained TSDB subsystem needs it; this is a source-selection decision,
not a claim that the original build left the macro undefined. It must also
leave both file modes, `FDB_KV_AUTO_UPDATE`, and `FDB_DEBUG_ENABLE` undefined.
`FDB_PRINT` is a separate Even logging seam.

## Safe promotion sequence

1. Build host-side layout probes with 32-bit types and short enums; require
   every recovered `sizeof`/`offsetof` value above.
2. Implement the Even `norflash` FAL port with read-only capability first.
   Keep program, erase, format, and automatic recovery unreachable.
3. Represent the recovered default-KV tables in openCFW-owned schema code;
   keep the resolved `kvbooCount` lifecycle and all Even migration, `NV`, and
   `db_api` policy outside the upstream directory.
4. Authenticate a non-mutating golden capture of both partitions and compare
   headers, status bits, CRC behavior, and complete key/value enumeration
   against the upstream source on a copy.
5. Admit source mount/read/iterate paths only after stock/source oracle
   parity. Enable mutation only after disposable-copy power-loss, GC,
   corruption, migration, and factory-reset tests.

It is now safe to **compile** a source-owned, fail-closed read-only FAL adapter
that returns negative transport errors and has no reachable program/erase
operation. It is not yet safe to invoke the stock mount/init path in a
production artifact: init can reach magic/corruption-driven
`fdb_kv_set_default`, and no authenticated external-flash golden capture has
established on-disk oracle parity. The remaining blockers are the one runtime
default word, first-party schema semantics, a non-destructive mount policy,
and the golden capture—not unidentified upstream FlashDB code. This audit
does not sign, flash, connect to, or mutate hardware.
