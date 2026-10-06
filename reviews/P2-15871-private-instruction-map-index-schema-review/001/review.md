# P2-15871 independent review

The captured list of 4,908 instruction files matches the current scan with no additions or removals. Fresh replay of the expanded schema reproduces 3,033 main-image byte matches, 1,875 unindexed files, 163,008 deduplicated coincident bytes, and 368 intervals. The matched index records and byte union are identical to the earlier diagnostic.

The expanded unindexed breakdown is 1,848 outside the main flash mapping, 2 unsupported top-level objects, 4 parse errors, 7 `bytes`-as-list records, 13 missing `bytes` keys, and 1 unsupported block shape. Thus 491 files previously rejected as unsupported block/top-level now parse far enough to classify as outside the main mapping; the matched count and union do not change.

**Correction to P2-15869:** its sentence describing all 1,875 unindexed files as outside the supported schema was too broad. The earlier breakdown was 1,357 outside mapping, 447 unsupported block, 67 unsupported top-level, and 4 parse errors. Preserve that receipt as historical; use this report for the revised breakdown. Neither index establishes ownership, code classification, semantic coverage, or canonical admission. Status remains partial and unaccepted.
