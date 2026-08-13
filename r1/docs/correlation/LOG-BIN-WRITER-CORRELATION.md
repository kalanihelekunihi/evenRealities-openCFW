# R1 `log.bin` writer correlation

## Disposition

Three formerly unclassified functions / 876 executable bytes are admitted as the R1-specific
`log.bin` partition geometry, initialization scan, and bounded circular-page append policy. No
third-party implementation has been identified for this orchestration. The functions are
therefore `r1_product_specific` / `clean_room_behavior_only`.

The implementation boundary is intentionally narrow. FAL 0.5.99's authenticated
`fal_partition_find` and `fal_flash_device_find` bodies remain compiled from the FlashDB 2.0.0
provider, the configured flash device continues to own physical read/write/erase operations, and
Nordic SDK 17.1.0 continues to own logging. The structured-log encoder/live cache and the composite
virtual-file exporter/transport are separate boundaries.

## Exact closure

| Entry | Bytes | Role |
| --- | ---: | --- |
| `0x0005908C` | 14 | partition sector-count accessor |
| `0x000590AC` | 258 | `log.bin` partition/provider lookup and erased-page scan |
| `0x00059670` | 604 | bounded circular-page append and pre-erase policy |

The closure totals three functions / 876 bytes. Every complete body hash and direct Thumb caller
set is frozen by `summarize_r1_log_bin_writer.py`. The writer has one direct caller: the manual
periodic-persistence function's call at `0x000914D2`. Initialization is called by the writer and by
the separately bounded virtual-export metadata path. The sector-count accessor has four calls
across initialization, writing, and virtual export.

## Recovered storage contract

The FAL partition record names `log.bin` on `device_flash`, begins at relative offset `0x18000`,
and is `0xC000` bytes long: twelve 4,096-byte sectors. Sector state is probed at byte offset four,
not at the first word; `0xFFFFFFFF` there denotes an erased sector.

Initialization resolves the partition and its named flash device through upstream FAL, clears the
local cursor, and scans sector probe words in order. It selects the first erased sector with offset
zero. If all sectors are non-erased it falls back to sector zero. A missing partition or flash
device leaves the writer unavailable.

The append path rejects null/zero-length input and input over 4,096 bytes. On first use it performs
the initialization scan. If a chunk would cross the current page, it advances modulo the actual
partition sector count, resets the in-page offset, and erases the selected page only if its probe
word is non-erased. After a successful provider write it advances the exact byte offset, examines
the following page, and pre-erases that page when necessary. Every erase/write address is checked
against the FAL partition bounds before the provider operation.

## Provider and safety exclusions

The clean-room implementation may reproduce the documented cursor and page-selection policy, but
must call rather than recreate:

- pinned FAL 0.5.99 partition/device lookup;
- the configured flash device's read, write, and erase callbacks;
- Nordic SDK 17.1.0 logging; and
- the separately admitted structured-log cache/periodic-persistence behavior.

This closure does not implement the composite private-log virtual file, BLE fragment sender, raw
flash API, arbitrary erase control, or signing/security bypass. The summarizer is static, reads no
private log content, and exposes no live sender or flash-mutation interface.

## Reproduce

```sh
python3 scripts/firmware/summarize_r1_log_bin_writer.py
python3 scripts/firmware/build_r1_source_ownership.py --check
python3 scripts/firmware/verify_openr1.py
```
