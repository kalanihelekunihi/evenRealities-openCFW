# R1 sleep synchronization marker in ordinary C

The backend at `0x5b6f4` now uses C to match acknowledged headers and program their four-byte synchronization marker. It retains the existing 12-byte sleep-context owner, including its source declaration, section flags, alignment and cold-zero bytes. No persistent state is added.

Null rows or zero length retain the native error diagnostic. Otherwise the row count is `(length/12)&255`; partial trailing rows are ignored and a quotient of 256 wraps to zero. Each row holds a captured header address and two expected fields. The 24-byte scratch header initializes once and retains bytes across partial or failed reads. The two expected row fields reload after the read callback.

A match writes `11223344` at the captured address plus 20, using a freshly loaded write callback. A failed write logs the live row address separately for each diagnostic channel and continues to later rows. Read status is ignored, as stock.

Validation passes 24,080 stock/C comparisons covering all 228 native instruction bytes, every byte-sized row count, count/address wrap, both match fields, partial reads, unaligned rows, live device/input changes and logging variants. Another 6,912 cases execute the C record/event storage path followed by acknowledgement marking against a mutable flash model. Final flash bytes and ordered calls/logs match. Nine compiled defects are rejected.

The tested object matches the normal build. The other 852 prior nongenerated objects, strong-symbol set, manifest, source-plan selections, imports and persistent state remain unchanged: 863 compiled units, 63 application imports and 22 bootloader imports. The actual context owner executes in both fixtures.

[The receipt](sleep-sync-marker-pure-c-review.json) records hashes and proof boundaries. FAL I/O, logging and health notification are modeled in the integration fixture. The bytearray model does not establish NOR bit transitions, physical persistence, power-loss behavior, concurrency, final application linking or boot. Other firmware assembly remains separate work.
