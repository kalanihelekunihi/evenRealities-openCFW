# P2-15869 independent review

Before replay, the captured input list of 4,908 `instructions.json` files exactly matched the current scan: no files had been added or removed. Fresh isolated replay found 3,033 files whose supported list/block instructions byte-match the locked main image and 1,875 files outside the supported schema. Deduplicating matching ranges yields 163,008 bytes across 368 intervals. Record hashes, pseudocode hashes, skipped records, and the interval union match the captured outputs. No revision filtering is applied, so superseded and incorrect interpretations remain in the index.

The counts describe byte coincidence and parser coverage only. They do not prove ownership, code classification, semantic correctness, or canonical coverage admission; “unindexed” means unsupported by this script, not that analysis is absent. Status remains partial and unaccepted.
