# R1 persistent storage formats (stock 2.2.6.0009)

> **Citations.** Repository paths cited as `path` or `path:line` refer to the tree at commit `832137ec`. The 2026-09-29 cleanup retires many of those evidence files; after they are removed, `git show 832137ec:<path>` still shows them.


All partitions live in the internal-flash `device_flash` FAL region at `0x000D4000`; the table is
in `memory-map.md` section 3. Each partition has one owner:

- `health.db` uses upstream FlashDB 2.0.0 TSDB.
- `kv.bin`, `sleep.db`, `ep.bin` and `log.bin` use R1 product formats.
- `pKey.bin` belongs to the GoMore integration.

Bond storage is separate: it uses Nordic FDS in the three pages at `0x000D1000`.

Tags: **Proven**, **Strong**, **Inferred**, **Unverified**. Sources are repository-root paths with
line numbers. Several header sources (`r1/src`, `r1/include`) are scheduled for deletion; their
constants are copied here.

## 1. `kv.bin`: fixed-class snapshot store (8 KiB, 2 sectors)

The format is R1 product code, not FlashDB KVDB.

Stock code:

| Address | Role |
|---|---|
| `0x00094E3C` | initializer |
| `0x000731A0` | class registration |
| `0x00073220` | class restore |
| `0x000734E8` | snapshot store |
| `0x00091780` | one-class writer |
| `0x00095168` | latest-snapshot reader |
| `0x00095304` | snapshot writer / rollover |
| `0x00057D0C` | startup scrub |
| `0x00064B24` | latest-slot scan |

Source: `r1/docs/correlation/KV-STORE-CORRELATION.md:5-45`.

**Geometry** (Proven; `KV-STORE-CORRELATION.md:5-27`; `r1/docs/reference/r1-capability-matrix.csv:109` (R1-108)):
- The partition holds 4 snapshots of 2,048 B, two per 4 KiB sector.
- Each snapshot has 8 blocks of 256 B. Blocks 0–6 are classes; block 7 is unused in stock.
- Each block is a 24-byte header followed by the payload.

**Classes** (Proven):

| Block | Name | Payload | Initial state / low flags |
|---:|---|---:|---|
| 0 | `dev_info` | 52 | 1 / 0 |
| 1 | `ble_mult` | 90 | 1 / 0 |
| 2 | `health` | 12 | 1 / 0 |
| 3 | `hsync` | 24 | 1 / 0 |
| 4 | `power` | 4 | 1 / 2 |
| 5 | `nv_r1` | 124 | 1 / 2 |
| 6 | `r_size` | 1 | 1 / 2 |

**24-byte class header** (Proven for field set; offsets from `r1/src/r1_kv_store.c:262-282`, matching the stock record per `KV-STORE-CORRELATION.md:29-31`):

| Off | Size | Field |
|---:|---:|---|
| 0 | 4 | base-131 hash of the 8-byte NUL-padded name (`h=h*0x83+c`; stock `0x0005D8CC`) |
| 4 | 8 | name |
| 12 | 4 | magic `0x45503130` (`"01PE"`) |
| 16 | 2 | state |
| 18 | 2 | flags: bit1 = low flag (dirty/other), bits 2+ = block index |
| 20 | 2 | payload length |
| 22 | 2 | CRC-16/MODBUS over the payload (stock `0x0005D87C`) |

**Stock semantics** (Proven; `r1-capability-matrix.csv:109`):
- Any dirty class causes all seven classes to be written.
- The latest snapshot is found by scanning slots 3..0 using only the class-0 magic. There is no
  snapshot checksum.
- Per-class restore checks the hash, the name and the CRC over the descriptor length. It does not
  check the stored length or the later magic.
- After four snapshots both sectors are erased before slot 0 is reused. A power loss during that
  window can lose data.

**Known class payload fields** (Strong):

| Class | Field | Source |
|---|---|---|
| `dev_info` byte 24 | bit `0x04` = ring-bound flag, cleared by removeRingNotify; bit 1 = REG1 DC/DC setting | `r1/docs/SECURITY.md:148-150`; `r1-capability-matrix.csv:197` |
| `dev_info` offsets 8 and 14 | two 6-byte peer address slots (advStart targets) | `r1/docs/SECURITY.md:149-150` |
| `dev_info` offset 20 | marker `CAMH` | `r1/docs/SECURITY.md:150` |
| `dev_info` | global-health bit and timestamp; power-recovery word (`2 | (mV & 0x3FFF)<<2`) written by `AT^PMIC_OFF` | `r1/docs/correlation/FACTORY-PMIC-HANDLERS-CORRELATION.md:25-33` |
| `hsync` | 6 x u32 LE: four named cursors (HR/SpO2/HRV/activity); words at offsets 8 and 20 unresolved | `KV-STORE-CORRELATION.md:90-94`; `r1/docs/correlation/HEALTH-DATABASE-STARTUP-CORRELATION.md:106-107` |
| `power` | +0 battery type (1..4); +2 signed ADC voltage compensation (applied only for −299..299) | `r1/include/openr1/r1_nv_recovery.h:23-24`; `r1-capability-matrix.csv:84` |
| `nv_r1` (124 B) | 15-byte product serial (erased = `FF`); +`0x3E` 6-byte temperature calibration; +`0x44` 6-byte accelerometer calibration; +`0x70` factory marker `0x55` (selects `_FAC` advertising); ship-mode marker `0x5A` | `r1/include/openr1/r1_nv_recovery.h:16-26`; `r1/docs/correlation/FACTORY-F2-HIGH-RISK-CORRELATION.md:14`; `r1/docs/README.md:813` |
| `r_size` | 1 byte ring size; valid 6..15 | `KV-STORE-CORRELATION.md:57-58` |

**NV recovery** (system `0x11`): a 116-byte identity/calibration body with CRC-16/MODBUS.
Fill-only merge into `nv_r1`, `power` and `r_size`. The compiled-default restore table at
`0x0009A0F8..<0x0009A432` holds 59 rows with 12-byte keys
(`r1/docs/PROVENANCE.md:32-33`; `r1_nv_recovery.h:12-33`). Tag: Proven.

openR1 deviation, not stock: block 7 carried an `r1_meta` generation/commit record. Blocks were
written 1–6, then 7, then 0, and sectors alternated (`KV-STORE-CORRELATION.md:61-78`). A
byte-identical build must reproduce the stock writer, not this one.

## 2. `health.db`: FlashDB 2.0.0 TSDB (24 KiB)

Startup orchestrator `0x00070030..<0x0007023E` (526 B, SHA-256 `67cf421c…55db`), singleton
accessor `0x00070028` (bytes `00 48 70 47`)
(`r1/docs/correlation/HEALTH-DATABASE-STARTUP-CORRELATION.md:5-24`). Tag: Proven.

| Item | Value | Source |
|---|---|---|
| DB name / partition | `"health"` at `0x00070268`, `"health.db"` at `0x0007025C` | `HEALTH-DATABASE-STARTUP-CORRELATION.md:35-37` |
| Max record length | 128 | same `:35-36` |
| Schema gate | six 16-byte schema descriptors; sum of byte 1 + 8 < 129 (≤120 schema bytes) | same `:30-32` |
| Control calls | `fdb_tsdb_control` 2 (SET_LOCK) then 3 (SET_UNLOCK), then `fdb_tsdb_init` | same `:33-38` |
| Time listeners | channels 1 then 0 | same `:39-40` |
| Recovery | iterate `[local_day_start, now]` into a zeroed 128-byte workspace, then crash-snapshot restore | same `:45-53` |
| FlashDB mode | TSDB, FAL mode | `r1/port/fdb_cfg.h:4-5` |
| Write granularity | 32 bits | `r1/port/fdb_cfg.h:6`; `r1/docs/correlation/STORAGE-PRODUCTION-WIRING-CORRELATION.md:120` (Inferred from build parity; not image-pinned) |

**128-byte hourly body** (Proven layout; 50 populated + 78 reserved bytes; `r1/include/openr1/r1_health_db.h:10-45`):

| Off | Size | Field |
|---:|---:|---|
| 0 | 2 | UTC offset minutes (s16) |
| 2 | 2 | reserved |
| 4 | 4 | recorded timestamp (u32) |
| 8 | 3 | HR avg/max/min (u8) |
| 11 | 3 | SpO2 avg/max/min |
| 14 | 3 | temperature avg/max/min |
| 17 | 3 | stress avg/max/min |
| 20 | 24 | activity packed, 6 x u32 (six 10-minute buckets) |
| 44 | 6 | HRV avg/max/min (u16) |
| 50 | 78 | reserved tail (preserved) |

The offsets are Inferred from the struct order with natural packing, which gives 50 bytes. The
struct is declared with fields in this order and a 50-byte populated size.

FlashDB function map (33 entries), e.g. `fdb_tsdb_init` `0x00063814`, `fdb_tsl_append`
`0x00063A28`, `fdb_tsl_iter_by_time` `0x00063AD8`, `tsl_append` `0x00093744`
(`r1/docs/correlation/FLASHDB-FAL-CORRELATION.md:29-52`). The 2.0.0 discriminator is reverse
iteration when `from > to` (`FLASHDB-FAL-CORRELATION.md:14-22`). Tag: Proven.

## 3. `sleep.db`: R1 circular journal (8 KiB, 2 sectors)

Stock:

| Address | Role |
|---|---|
| `0x0008FC6C` | sector-state predicate |
| `0x0008FE28` | first-writable finder |
| `0x0008FE98` | appender (body before header) |
| `0x000901E4` | closer (close words, minimum-sequence rollover) |
| `0x0005B6F4` | sync marker `0x11223344` (timestamp checked) |
| `0x0008DD8C` → `0x0005B18C` | FAL bind |

Sources: `r1/docs/PROVENANCE.md:106-109`; `STORAGE-PRODUCTION-WIRING-CORRELATION.md:22-24`.
Manifest identity `r1-sleep-journal` is "ring-specific circular journal rather than FlashDB TSDB"
(`third-party/fetched/manifest.json`).

Layout (from the openR1 implementation; values marked Strong where the stock correlation names them):

| Item | Value | Tag | Source |
|---|---|---|---|
| Sectors | 2 x 4096 | Strong | `r1/include/openr1/r1_sleep_db.h:10-11` |
| Sector header | 16 B: close word0 `0xCCFFAABB`, word1 `0x66889977`, u32 close sequence, u32 0 | Strong | `r1_sleep_db.h:13,18-19`; `r1/src/r1_sleep_db.c:139-143` |
| Record headers | up to 8 per sector, 24 B each, starting after the sector header (bodies start at `208`) | Strong | `r1_sleep_db.h:12,14-15` |
| Record header | +0 u16 aligned length; +2 u16 body offset; +4 u16 state; +6 s16 UTC offset (body+10); +8 u32 start (body+12); +12 u32 end (body+16); +18 u16 CRC-16/MODBUS of body; +20 u32 sync marker `0x11223344` | Strong (field set) | `r1/src/r1_sleep_db.c:253-281,333-352` |
| Max append / sync read | 3,888 B / 232 B | Strong | `r1_sleep_db.h:16-17`; `PROVENANCE.md:105` |
| Admission | ≥3,600 s sleep; append-success triggers auto sync argument 6; two-attempt journal policy; stock erases the DB after repeated failures | Proven | `PROVENANCE.md:108`; `r1/docs/SECURITY.md:25-29` |

openR1 choice, not stock: the state values `0xFFFE` (reserved) and `0xFFFC` (committed), and the
reserve-then-commit ordering (`r1_sleep_db.h:21-22`; `r1/docs/SECURITY.md:25-29`). Stock writes
the body before the header, without a separate commit bit.

## 4. `log.bin`: circular page log (48 KiB, 12 sectors)

Stock writer closure (`r1/docs/correlation/LOG-BIN-WRITER-CORRELATION.md:26-54`). Tag: Proven:

| Address | Bytes | Role |
|---|---:|---|
| `0x0005908C` | 14 | sector count |
| `0x000590AC` | 258 | init scan |
| `0x00059670` | 604 | append |

- **Erased-sector probe**: a sector counts as erased when the word at byte offset 4 is
  `0xFFFFFFFF`.
- **Initialisation**: the cursor goes to the first erased sector. If none is erased, it uses
  sector 0.
- **Append**: input is limited to 1..4096 B. When a write would cross a page, the cursor advances
  modulo 12 and the new page is erased only if it is not already erased. After each write the
  writer pre-erases the next page if needed.
- **Caller**: a periodic persistence function at `0x000914D2` writes exactly one 4,096-byte page
  of the structured-log cache.

Structured-log cache (RAM): 8 KiB, 12-byte prefix, 32-byte arguments, 16-byte strings, mode bits
`0x01` storage and `0x80` immediate, persist gate 10,000 ticks
(`r1/include/openr1/r1_storage.h:25-35`; `r1/docs/PROVENANCE.md:81`). Tag: Strong.

## 5. `ep.bin`: event/parameter records (8 KiB)

- It holds 1,024 records of 8 bytes. The low nibble of byte 0 is magic `0xA`, and bytes 4..7
  hold a u32 LE timestamp.
- The first record without the magic becomes the first-free cursor.
- If every record has the magic, the cursor follows the greatest nonzero timestamp, with the
  later of two equal timestamps winning, modulo 1024.
- If every record has the magic and every timestamp is 0, the cursor is 1.
- Scan `0x0003EE34..<0x0003EF3C`, caller `0x0005E10A`
  (`r1/docs/correlation/FRONTIER-264-274-CORRELATION.md:33-39`; `r1/include/openr1/r1_storage.h:16-19`).
- Tag: Proven for cursor rules. The timestamp offset is Inferred.

## 6. Diagnostic virtual export file

The export concatenates these parts in order:

1. all 8,192 B of `ep.bin`;
2. each non-erased `log.bin` sector, in cyclic order starting after the first erased sector
   (order 0..11 if none is erased);
3. the frozen u16-length structured-log cache;
4. an optional crash C-string without its NUL.

The file is eligible if at least one log sector is non-erased or one EP record has the magic. One
CRC-32C (zero seed and xorout) covers the whole file. It is sent through pb_tran fragments
(`r1/docs/correlation/DIAGNOSTIC-EXPORT-CORRELATION.md:10-25`). Tag: Proven.

## 7. `pKey.bin`: GoMore key and prior state (4 KiB)

- Bound to FAL by `0x0006BA68` (`r1/docs/correlation/FRONTIER-128-202-CORRELATION.md:74-75`).
- GoMore pKey load/CRC diagnostics are at `0x0006AD80`; authorization parameter setup is at
  `0x0006B27C`.
- The key is Base64-decoded, decrypted with the dual-AES chain using two 32-byte keys held in
  flash, and must hold 4 comma-separated fields
  (`r1/docs/boundaries/GOMORE-PROVIDER-BOUNDARY.md:29-31`; `r1/docs/boundaries/GOMORE-AUTH-PARSER-PROVIDER-BOUNDARY.md:20-40`).
- A 736-byte GoMore prior-state record is appended through the recovered slot/compaction contract
  (`r1/docs/correlation/GOMORE-TOPIC-INPUT-CORRELATION.md:86-88`).
- The key is 64 bytes, delivered by setAlgoKey (`r1-capability-matrix.csv` R1-017).
- Tags: Strong for roles. The exact slot layout is Unverified here; see the reconstructed GoMore
  sources and the decompilation.

Dual-AES chain (R1 wrapper `0x00048B02` over tiny-AES-c inverse core):
1. Copy the input to the output buffer.
2. Decrypt blocks in reverse order with key half 2, with the tail chain seeded from key half 1.
3. Decrypt forward with key half 1, with the chain seeded from key half 2.

XOR helper `0x00098E22`, callback `0x000891A4`
(`r1/docs/correlation/TINY-AES-CORRELATION.md:33-42`). Tag: Proven.

## 8. RAM-retained records

| Record | Size | Notes | Source |
|---|---:|---|---|
| Health crash record | 966 B | magic, crash timestamp + validity bit, 52-byte cache summary, 896-byte opaque provider area, CRC-16/MODBUS | `r1/docs/PROVENANCE.md:71` |
| Retained crash log | 3,008 B | newline policy over `vsnprintf` + RTT | `PROVENANCE.md:80`; `r1/include/openr1/r1_retained_log.h:10-12` |

## 9. FDS (Peer Manager)

- There are three virtual pages (2 data + 1 swap on a live unit) at `0xD1000`, with
  `FDS_VIRTUAL_PAGES_RESERVED = 36` (Proven).
- The record key range is `0xC000..0xFFFE` (`record_key_within_pm_range` at `0x00064160`).
- Peer Manager keeps seven peer-data IDs and 256-peer bitmaps
  (`r1/docs/correlation/NORDIC-SDK-CORRELATION.md:463-490`;
  `r1/docs/closures/AUGUST-18-PHYSICAL-VALIDATION-BLOCKER.md:37-41`).
