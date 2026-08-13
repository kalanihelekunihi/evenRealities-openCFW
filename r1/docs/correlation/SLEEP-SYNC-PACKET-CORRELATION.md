# R1 sleep synchronization packet correlation

Status: 472-byte product function byte-pinned; bounded pure packet builder implemented.

The former frontier leader `0x0008DA24..<0x0008DBFC` converts the compact stored sleep record into
the public synchronization packet, then delegates allocation, transport, acknowledgement, and
release. Its exact body SHA-256 is
`d3804f3dd415358d10ced85de5f8cccc64da4db33d40e37830d05096b7b86ac5`; its sole direct caller is
`0x0008F9C2`. `tools/evidence/summarize_r1_sleep_sync_packet.py` authenticates all three facts and
the embedded `946080000` legacy-clock cutoff.

The first 32 bytes are the sleep header. Each compact input stage uses its low two bits as type and
high six bits as duration in half-minutes. Adjacent equal types are merged into one three-byte
`type, UInt16LE duration` output run. The output count at offset 30 is therefore the merged run
count, not the compact byte count.

For start times before `946080000`, the UTC offset is forced to zero. If a nonzero current time is
between the legacy start and future end, the end is clamped to current time. Modern records use the
current UTC offset and retain their end time. Reserved header byte 3 is zeroed, matching the stock
zero-initialized allocation.

`r1_sleep_build_sync_packet` in `r1/src/r1_health.c` implements this as a capacity-checked pure
function. It rejects zero-duration entries and overlong/truncated records instead of reproducing
the stock unbounded allocation behavior. It performs no allocation, clock read, flash access, BLE
send, acknowledgement mutation, or logging. Those services remain external provider/adaptor seams.

Tests cover adjacent-run merging, legacy timezone/end correction, modern offset/end preservation,
reserved-byte zeroing, exact wire bytes, and zero-duration rejection.

Reproduce with:

```sh
python3 tools/evidence/summarize_r1_sleep_sync_packet.py
make -C openR1 test
```
