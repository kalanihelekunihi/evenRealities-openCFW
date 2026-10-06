# Independent review P2-18495

Status: partial, unaccepted. No source or gate changes.

Fresh extraction from the pinned firmware confirms 30 bytes at `0x46061A..0x460638`: two zero alignment bytes followed by seven 4-byte little-endian words. The values are `0x200746E4`, `0x00762210`, `0x00787A80`, `0x0070CA64`, `0x0078B5B8`, `0x00762230`, and `0x00781250`. Candidate `data.bin` and `words.json` match the fresh replay.

I cross-checked PC-relative references in maps 18866/18868/18870 and 18880/18882/18890/18892/18894. They support the global pointer at 0x46061C, first and second diagnostic values at 0x460620/624 and 0x460630/634, and common argument literals at 0x460628/62C. The preceding POP return at 0x460618 and next function entry at 0x460638 bound the proposed data interval.

Only bytes and local reference provenance are established. No pointer contract, pointee layout, global ownership, or surrounding coverage is inferred. Partial/unaccepted only.
