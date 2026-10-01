# Independent review 2013

**Result:** PASS_SCOPED.

- Source and artifact hashes match the receipt; 0xA3B0..0xA440 is exactly the owned 144-byte function, with literal 0x20000F34 at 0xA440 outside it. Independent Thumb disassembly agrees with the recorded extent.
- Isolated replay reproduced all 42 fixture rows, including both indices, sorted/unsorted priority sequences, tie cases, head/link updates, result and stack checks.
- The loop continues scanning rather than stopping at the first higher-priority item, retaining the last qualifying successor. Equal priority is passed by the <= comparison; the separate head case inserts before only for strictly lower incoming priority.

**Limits:** Empty, invalid-field and duplicate insertion behavior is described from instructions but is not covered by this packet’s replay; dedicated boundary replay is pending. Cycles, arbitrary indices, concurrent mutation and physical callback effects remain unresolved. No canonical admission is made.
