# Activity day-merge and packet-flush correlation

## Outcome

Five product-owned functions assemble activity history from the current RAM cache and decoded flash
records, serialize one public day packet, and preserve acknowledgement context. Storage decoding,
allocation, transport, and clock/calendar conversion remain provider or caller boundaries. The
clean implementation accepts typed values after those boundaries and does not reproduce FlashDB,
FreeRTOS heap, EUS transport, or calendar-library code.

| Recovered extent | Size | Clean evidence name |
| --- | ---: | --- |
| `0x0003BCF8..<0x0003BD4C` | 84 | `r1_activity_acknowledgement_timestamp_clamp` |
| `0x0003BDAC..<0x0003BDD6` | 42 | `r1_activity_day_builder_reset` |
| `0x0003C304..<0x0003C4A2` | 414 | `r1_activity_ram_cache_merge` |
| `0x0003C578..<0x0003C796` | 542 | `r1_activity_day_packet_flush` |
| `0x0003C958..<0x0003CB04` | 428 | `r1_activity_flash_record_merge` |

The verifier pins all five Ghidra bodies by exact size and SHA-256.

## Builder and public packet

The stock builder is `0x49c` bytes: 144 presence bytes, 144 seven-byte public items, count, day
start, signed UTC offset, serial/context, acknowledgement callback, acknowledgement timestamp, and
mode. The portable `r1_activity_offline_packet` represents the same logical fields without copying
stock padding or private pointers. Reset clears the day contents and acknowledgement timestamp but
preserves serial, mode, and whether acknowledgement context is requested.

The clamp helper returns a nonzero candidate only when it is no later than firmware time;
otherwise it returns firmware time. Flush refuses to emit a builder whose acknowledgement
timestamp is in the future. A nonempty accepted builder is exposed through a caller callback in the
existing public layout: count, signed UTC offset, day start, and seven bytes per ascending bucket.
The clean callback replaces stock heap allocation and EUS send internals while retaining their
success/error boundary.

## RAM-cache merge

The RAM path rejects null/zero inputs, a stale window whose start is at or after current time, and
a requested day in the future. It updates the logical cache day and signed offset, temporarily
selects ACK mode two, and scans all 144 ten-minute buckets. The current bucket index is
`(now - dayStart) / 600`, clamped to 143. Caller-supplied live step, active-kilocalorie, and total-
kilocalorie deltas are added only to that bucket with UInt16 wrapping.

The current bucket is eligible regardless of the lower window bound. Other nonzero buckets are
included only when `windowStart <= dayStart + index*600 <= now`. The greatest included bucket time
becomes the clamped acknowledgement timestamp and the completed builder is flushed immediately.
The caller's original mode is restored after the operation.

## Decoded flash-record merge

The clean flash boundary accepts one decoded record containing signed UTC offset, record timestamp,
and six packed 12/10/10-bit words. It skips future records before touching the builder. Local hour
and day start are derived from timestamp plus offset; a record exactly at local midnight belongs to
hour 23 of the preceding local day, matching the recovered rollover rule. An optional gate limits
the input to days earlier than the current local day.

A change of local day or UTC offset flushes an existing builder before starting another. Within a
day, each nonzero word maps to `hour*6 + withinHour`. Flash records fill only previously absent
buckets, unlike the offline queue where a later duplicate replaces a bucket. The maximum accepted
record timestamp becomes acknowledgement context. Callers explicitly flush any remaining builder
after iteration.

## Clean-room hardening and tests

The clean API never reads private SRAM, decrypts or parses FlashDB records, allocates memory, or
invokes transport directly. It validates all required pointers and represents clock, calendar,
live accumulator, decoded storage, and emission results as typed inputs. Tests cover timestamp
clamping, context-preserving reset, future-ACK drop, exact encoded lengths, midnight rollover,
previous-day filtering, non-replacing flash duplicates, day/offset transitions, RAM windowing,
current-bucket augmentation, mode restoration, and future-record rejection.

This family adds no motion or health algorithm, vendor register access, BLE command, signing
bypass, or deployment change.

The retained Nordic APIs link at `0x00033670` (clamp), `0x0003367C` (reset), `0x00033694`
(flush), `0x000336F0` (RAM merge), and `0x00033830` (decoded-flash merge). The retained health
table is at `0x0003B274`. The verified unsigned application is 94,804 bytes text, 236 bytes data,
and 132,544 bytes BSS. Its HEX and BIN SHA-256 values are
`48e1b3fadfdb956fbdf5f637d48c9a5808db5394848fb4538450c0ff98be80cf` and
`421a42cf37dad04dadcff5d3b1742efcba4ba50fd1d2e52f26bcf00e5df24d35`.
