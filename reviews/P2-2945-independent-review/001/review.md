# Independent review 2945/001

**PASS_SCOPED**; `accepted` remains false.

The isolated scan replays and all 33 image hashes match the authenticated inventory. It reports one direct boot-flash call candidate. Decoding the original bytes confirms `BL 0x42B6B8` at `0x42BCEC` (encoding `fff7e4fc`). Raw aligned/unaligned word occurrences remain candidate evidence only.

This is a navigation scan, not caller-ownership proof or a completeness claim. Indirect/computed references, other instruction modes, and unscanned sources are not excluded.

Candidate receipt SHA-256: `0effc1510c04b43afbecf4dfc8d4edc6e33ae1cf0e722e2b8e9eb882dc6c33d0`.
