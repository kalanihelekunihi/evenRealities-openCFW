# Activity offline-sync correlation

## Outcome

The R1 activity subsystem has a product-owned offline synchronization queue between its packed
ten-minute accumulator and the public activity-history path. It is not a motion-classification or
health-algorithm provider: it stores already-produced 12/10/10-bit activity words, groups them into
public day packets, and retires an acknowledged FIFO prefix. The recovered strings, dedicated SRAM
layout, direct callers, public packet shape, and first-party executable model jointly support a
clean-room implementation without admitting GoMore, Goodix, or accelerometer-provider code.

## Recovered boundary

| Recovered extent | Size | Clean evidence name | Role |
| --- | ---: | --- | --- |
| `0x0003BDD8..<0x0003BE66` | 142 | `r1_activity_offline_queue_consume` | clears the oldest timestamp-bounded FIFO prefix |
| `0x0003BED0..<0x0003BEDE` | 14 | `r1_activity_offline_queue_empty` | returns whether count is zero |
| `0x0003BEE4..<0x0003BFD6` | 242 | `r1_activity_offline_queue_enqueue` | validates time, writes a record, and overwrites oldest on full |
| `0x0003C0D8..<0x0003C1E8` | 272 | `r1_activity_sync_acknowledgement` | handles flash, offline, and current-RAM acknowledgement modes |
| `0x0003CB80..<0x0003CCCE` | 334 | `r1_activity_offline_queue_merge` | groups FIFO records into consecutive day/offset packets |

Ghidra omitted the acknowledgement callback as a function even though disassembly and the stored
Thumb callback pointer establish its complete entry and return boundary. It is therefore a
272-byte `manual_provenance_supplement`; the other four entries come from `functions.csv`. The
project verifier pins all five bodies by size and SHA-256.

## Storage and queue semantics

The stock metadata is three bytes at `0x200067A8`: read index, write index, and count. Its record
storage begins at `0x20015A6C` and contains 144 records of exactly 16 bytes:

| Offset | Width | Meaning |
| ---: | ---: | --- |
| `0x00` | 4 | packed activity word: steps 12 bits, active kcal 10 bits, all kcal 10 bits |
| `0x04` | 4 | local-day start timestamp |
| `0x08` | 4 | recorded timestamp |
| `0x0C` | 2 | signed UTC offset in minutes |
| `0x0E` | 1 | absolute ten-minute bucket index, `0...143` |
| `0x0F` | 1 | retained tail byte; enqueue does not write it |

Enqueue drops an all-zero packed word, a recorded timestamp later than the sampled firmware time,
or a local-day start later than that time. A full queue remains at count 144 and advances both the
write index and the oldest read index. Consumption clears complete 16-byte records only while the
oldest recorded timestamp is at or before the acknowledgement cutoff; it stops at the first newer
record, preserving FIFO-prefix semantics.

Merge walks records in FIFO order. Zero and future records are skipped. A change in either day
start or UTC offset flushes the current packet, so grouping is by consecutive runs rather than a
global key sort. Within one packet, a repeated bucket replaces the earlier 12/10/10-bit values
without increasing the bucket count. The packet acknowledgement timestamp is the maximum recorded
timestamp among its accepted entries. The encoded body remains the established public layout:
count, signed UTC offset, local-day start, then seven bytes per ascending bucket index.

Acknowledgement mode zero (flash history) and mode two (current RAM) advance the persistent
activity cursor only when the acknowledged timestamp is not in the future and is newer than the
current cursor. Mode one consumes the acknowledged offline FIFO prefix even when that timestamp is
later than the sampled firmware clock. Unknown modes preserve both cursor and queue.

## Clean implementation and intentional hardening

`r1_activity_offline_queue` reproduces the 144-record topology and 16-byte record layout.
`r1_activity_offline_enqueue`, `r1_activity_offline_consume_through`,
`r1_activity_offline_merge`, and `r1_activity_offline_acknowledge` implement the observed behavior.
The caller supplies merge workspace and an emission callback, avoiding a hidden allocation or a
large task-stack object. The existing `r1_activity_encode_daily` performs public serialization.

Unlike the stock callbacks, openR1 checks every bucket index and verifies the read/write/count
invariant before accessing storage. Corrupt state returns an error rather than indexing outside the
queue or 144-bucket packet. Tests cover all drop reasons, retained byte 15, full-ring overwrite,
prefix consumption, duplicate replacement, future-entry filtering, exact encoded bytes, all
acknowledgement modes, and corrupt-state rejection.

The verified Nordic link retains the empty, enqueue, consume, merge, and acknowledgement APIs at
`0x00033086`, `0x00033098`, `0x000332C8`, `0x0003332C`, and `0x00033466`. The resulting unsigned
application is 90,956 bytes text, 236 bytes data, and 132,456 bytes BSS. Its standalone HEX and BIN
SHA-256 values are `0954a9375874ee4f88139ba6243e20e1afba122e67afccba9d410e638053fa81` and
`31f3a97de9805239b03c51297f1de2ea9eaeff6fee372f1ea1f0c0a5c2f7bc91`.

This component does not expose private SRAM, internal event injection, raw motion samples, or a
new BLE command. It does not alter authorization, signing, boot verification, rollback, ACL,
APPROTECT, or deployment behavior.
