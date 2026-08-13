# G2 FlashDB service-adapter recovery

Status date: 2026-08-11  
Target: official G2 `s200_v2.2.6.10` Apollo-main image  
Retained path: `platform\service\flashDB\db_api\service_db_api.c`

## Result

The complete linked object is closed at `[0x00540ED0,0x005412E0)`: eleven
functions contribute 908 executable bytes and one trailing pool contributes
132 bytes, for 1,040 physical bytes. The original retained-path census found
five functions / 462 bytes. Focused recovery adds the FAL initializer, erase
callback, mutex lock, blob-write wrapper, database-object accessor, and service
initializer. No executable or pool byte inside the object remains unassigned.

This is a first-party adapter, not a hidden FlashDB translation unit. Its 59
external calls terminate at 45 EasyLogger diagnostics, seven exact
CMSIS-FreeRTOS wrappers, two FlashDB 2.1.1 KVDB APIs, and five first-party
NOR-flash/database providers. It embeds zero third-party definitions and adds
no new dependency family or version discriminator.

## Complete object

| Stock interval | Recovered identity | Bytes | Evidence and role |
|---|---:|---:|---|
| `0x00540ED0..0x00540ED4` | `_flashDBInit` | 4 | FAL callback table; returns zero |
| `0x00540ED4..0x00540F2C` | `_flashDBRead` | 88 | Exact diagnostic name; NOR read adapter |
| `0x00540F2C..0x00540F84` | `_flashDBWrite` | 88 | Exact diagnostic name; NOR write adapter |
| `0x00540F84..0x00541088` | `_flashDBErase` | 260 | Exact diagnostic name; 4-KiB erase loop |
| `0x00541088..0x005410DA` | `_flashDBMutexInit` | 82 | Exact diagnostic name; `osMutexNew` |
| `0x005410DA..0x00541126` | `_flashDBMutexLock` | 76 | Stored DB callback; forever acquire |
| `0x00541126..0x0054116E` | `_flashDBMutexUnlock` | 72 | Stored DB callback; mutex release |
| `0x0054116E..0x005411F2` | `SVC_FlashDBBlobRead` | 132 | Exact retained name; `fdb_kv_get_blob` signature |
| `0x005411F2..0x00541232` | `SVC_FlashDBBlobWrite` | 64 | Sibling `fdb_blob` construction and `fdb_kv_set_blob` signature |
| `0x00541232..0x00541240` | `SVC_FlashDBGetObject` | 14 | Returns `0x2005DFFC + index * 0x8AC` |
| `0x00541240..0x0054125C` | `SVC_FlashDBInit` | 28 | Initializes the mutex, then `sysenv` and `factory` |

The body concatenation hashes to
`4543128905f9c50185a34ca423ad0e0ed0ac61f1a8d0847d18a501cbe20a13bc`.
All 366 decoded instructions reproduce the body bytes, with instruction-map
digest `b0a59eced9c0d53c471563d4a861a905331c4600562a947eab8f3f094174d2ca`.
The trailing pool hashes to
`175570b9821b29ab5e79ac426a166db7975a8c3f2544351b1fc1c1aef0a032ff`;
the complete physical object hashes to
`5bc673adf9a8d39874f81329837fabfca45dbeab8d5af0d1c16b799e784cc4c4`.

The ingress census finds 23 direct BL entry sites and no strict-interior BL
target. Six stored Thumb pointers close the two callback families:

- `0x005412D8` and `0x005412DC` select the mutex lock/unlock functions.
- `0x00722B54..0x00722B60` select FAL init/read/write/erase.

Nine raw references to the retained path originate in seven functions. The
five baseline source-path anchors remain the conservative frontier metric;
the six restored functions increase complete-object coverage without
inflating that path-anchored lower bound.

## Third-party origin, version, and commit

The two KVDB calls map exactly by signature and behavior:

- `0x0054454A` is `fdb_kv_get_blob`.
- `0x0054503A` is `fdb_kv_set_blob`.

The retained firmware reports FlashDB 2.1.1. OpenCFW's authenticated source
oracle is the upstream `2.1.1` tag at commit
`714d6159e7e6afb267a3953756abca445c350e61`. The vendored snapshot contains
the exact public declarations and KVDB implementation. The firmware proves
the version and the recovered source/configuration behavior, but does not
prove that Even used an unmodified checkout of that public commit. The commit
is therefore the reproducible source baseline, not an asserted historical
generating commit.

The seven RTOS edges are four calls to `osKernelGetTickCount` and one each to
`osMutexNew`, `osMutexAcquire`, and `osMutexRelease`. All are already
source-owned from CMSIS-FreeRTOS v10.5.1 commit
`d213f261b5be6bb29a7cce8b84071706b72f4d53`. EasyLogger diagnostics terminate
at the admitted 2.2.99-compatible core selected at
`a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24`.

This consumer object consequently strengthens the existing FlashDB and
CMSIS-FreeRTOS admissions but cannot narrow either historical checkout: all
observed calls and ABIs are already explained by the selected sources.

## OpenCFW boundary

The stock FAL adapter must not be copied literally into a writable OpenCFW
build. `_flashDBRead`, `_flashDBWrite`, and `_flashDBErase` return zero when
the first-party NOR driver fails. FlashDB 2.1.1 maps only negative FAL returns
to `FDB_READ_ERR`, `FDB_WRITE_ERR`, or `FDB_ERASE_ERR`; zero can therefore
conceal a device failure. A source-owned port must translate every driver
failure to a negative callback result.

The source baseline, DB layout, and callable dependencies are locally closed.
The remaining FlashDB gates still require unavailable or external evidence:

- a read-only golden capture of the external flash and power-loss testing;
- a deliberate non-destructive mount/schema policy;
- an explicit decision before routing any erase or wholesale-default path.

The later system-KVDB closure resolves the former `kvbooCount` item: the
startup default is zero and initialization performs a persisted
read/increment/write sequence. See
[`g2-service-kvdb-recovery.md`](g2-service-kvdb-recovery.md).

The object remains analysis-only and is not production-routed.

## Reproduction

Run:

```sh
make service-db-api-closure
```

`tools/analyze_g2_service_db_api.py` authenticates the official image and all
three object manifests, re-decodes every instruction, replays direct and
stored ingress, validates provider accounting, and composes
`tools/analyze_g2_flashdb.py` so the version, ABI, callback, partition, and
error-seam findings cannot drift independently.
