# Activity daily-cache correlation

## Outcome

Five product-owned functions adapt the 144 packed activity buckets to the daily-storage
interface. They contain no motion classification or third-party health algorithm. The clean
implementation resets a day, reads one six-bucket hour under the recovered legacy-clock policy,
and writes one hour, while reusing the separately admitted activity offline queue.

| Recovered extent | Size | Clean evidence name |
| --- | ---: | --- |
| `0x00048288..<0x000482A6` | 30 | `r1_activity_daily_cache_reset` |
| `0x000482A8..<0x00048324` | 124 | `r1_activity_daily_cache_read` |
| `0x0004832C..<0x0004834A` | 30 | `r1_activity_daily_cache_write` |
| `0x0005A9F0..<0x0005A9F4` | 4 | `r1_activity_daily_cache_accessor` |
| `0x0005A9F8..<0x0005AA0E` | 22 | `r1_activity_daily_cache_refresh_metadata` |

The verifier pins all three Ghidra bodies by size and SHA-256. Reset clears exactly the 576 packed
bucket bytes, writes the signed UTC offset at cache offset `0x240`, and writes local-day start at
`0x244`; the two intervening bytes are outside the portable logical model and are not assigned a
meaning. Write copies one exact 24-byte hour. OpenR1 adds bounds checks that the stock callbacks do
not perform.

Read first copies the requested hour. It returns that copy unchanged when firmware time status is
nonzero, the sampled time exceeds the legacy cutoff `946080000`, or all six packed words are zero.
Otherwise it interprets the signed offset bits as an unsigned value before division by 60, matching
the recovered callback. If that hour offset precedes the requested hour or a second clock sample
moves backward, the returned hour is zeroed. Each nonzero bucket is then enqueued with day and
offset zero, the first sampled timestamp, and an absolute index based on the adjusted hour; the
returned hour remains redacted whether enqueue accepts or rejects a timestamp.

`r1_activity_cache_reset`, `r1_activity_cache_read_hour`, and
`r1_activity_cache_write_hour` implement this behavior over caller-owned state. Derived portable
totals are recomputed on write and cleared on reset; this is an adapter invariant, not a claim that
the stock 584-byte cache contains those fields. Tests cover reset, write bounds, unchanged returns,
legacy cutoff, signed-to-unsigned offset behavior, backward-clock redaction, exact adjusted bucket
indexes, offline enqueues, redacted output, and timestamp-count validation.

The stock pointer accessor is represented by that caller-owned `r1_activity_history *` rather than
a private SRAM singleton. `r1_activity_cache_refresh_metadata` updates only the local-day start and
signed UTC offset, preserving all buckets, latest timestamp, and totals. Its tests prove this
non-resetting behavior. The two adjacent bodies are exact-hash pinned just like the callbacks.

The flash-record merge `0x0003C958`, RAM-cache merge `0x0003C304`, and day-packet flush
`0x0003C578` were subsequently admitted from their own function-local evidence; see
[`ACTIVITY-DAY-MERGE-CORRELATION.md`](ACTIVITY-DAY-MERGE-CORRELATION.md). They accept decoded,
caller-owned inputs and do not broaden this cache callback boundary.

The retained Nordic APIs link at `0x0003307A` (reset), `0x0003309A` (metadata refresh),
`0x000330A2` (write), and `0x000332EC` (read). They are included in the verified unsigned
application fingerprint documented by the top-level open-firmware README.
