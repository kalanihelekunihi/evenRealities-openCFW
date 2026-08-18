# R1 composite diagnostic-export correlation

## Recovered contract

Direct Thumb-2 inspection closes the stock composite source around six anchors:

| Entry | Recovered role |
| --- | --- |
| `0x00058D54` | stop the snapshot and release the EP/log writer guard |
| `0x00058D64` | start the snapshot and assert the writer guard |
| `0x00058DE4` | derive eligibility, total length, and whole-file checksum |
| `0x000590AC` | scan the twelve `log.bin` sectors |
| `0x000592BC` | read the composite virtual address space |
| `0x00059670` | append to the bounded `log.bin` store |

The file is exactly: all 8,192 bytes of `ep.bin`; each non-erased 4,096-byte
`log.bin` sector in cyclic order beginning after the first erased sector; the
frozen UInt16-length structured-log cache; and an optional valid crash C string
without its NUL. A sector is erased when its four-byte probe at offset `+4` is
all `FF`. If no sector is erased, order is `0...11`. Eligibility requires at
least one non-erased log sector or at least one EP record whose first-byte low
nibble is `A`. One non-reflected Castagnoli CRC-32, seeded and finalized with
zero, covers the exact concatenation.

The stock arbitrary reader has a physical sector-wrap edge. The clean-room
reader deliberately preserves the virtual bytes while splitting every
cross-segment and cross-sector request into valid provider reads.

## Transparent implementation

`r1_log_export_snapshot_prepare`, `r1_log_export_snapshot_read`, and
`r1_log_export_snapshot_finish` implement the complete source contract over the
typed `r1_flash` and structured-cache APIs. Preparation records sector order,
freezes the cache length, checks widened bounds, and computes the checksum
incrementally with `r1_crc32_castagnoli_update`; it does not allocate, mutate,
erase, or return a flash provider. Reads are length-bounded and can safely span
EP, multiple log sectors, cache wrap, and the optional crash tail.

The Zephyr adapter asserts the export-active guard before inspection and holds
one mutex across each storage operation. While active, typed/format log
production, direct log append, and periodic persistence are suppressed. Finish
always releases the guard. The target currently supplies no crash string
because it has no proven stock-equivalent valid C-string provider; the core's
optional tail is covered by host tests and is not synthesized from unrelated
reset or health snapshots.

## Authorization and transport boundary

The target exposes begin/read/finish only as retained internal C entry points.
`openr1_bae8_zephyr_diagnostic_export_*` requires the connection to be active,
encrypted, bonded, independently owner-authorized, and assigned the phone role
on every data operation. A single atomic owner prevents concurrent snapshots.
Disconnect, authorization loss, owner revocation, failed preparation, and
explicit finish release the storage guard so logging cannot remain frozen.

No GATT characteristic, protocol opcode, raw-flash command, erase control, or
undocumented start/data/raw/check sender is added. That BLE transport remains a
separate withheld capability until physical ATT behavior, retry/disconnect
timing, content consent, and redaction are validated on an owned ring.

## Verification

Host tests pin eligibility, erased/full-sector chronology, exact whole-file
CRC, EP-to-log and log-to-log boundary reads, cache/crash tails, range rejection,
and post-finish denial. The source-boundary gate requires all core, storage,
runtime-authorization, and BAE8 owner-wrapper entry points. Bundle packaging
then proves each is uniquely retained in the nRF52840 loadable image.

```sh
make -C r1 test sanitize arm-objects
python3 r1/tools/verify_zephyr_source_boundary.py
python3 r1/tools/verify_zephyr_bundle.py \
  r1/build/openr1-zephyr/openr1-source-built.zip
```
