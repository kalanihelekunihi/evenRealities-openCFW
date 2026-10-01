# Independent review 2191

**Result:** PASS_SCOPED.

All source, code, literal and receipt-file hashes match. The body [0x6BD4, 0x6D6A) and literal pool [0x6D6C, 0x6D74) are the same verified bytes as review 2189, and the listing matches an independently regenerated Thumb/M-class disassembly.

An isolated replay reproduced all 48 fixtures exactly. The cases vary modes 2/4, saved start and length matches/mismatches, descriptor values `0x10`, `0`, and `0x2010`, and callback null/non-null. Decoded instructions confirm fast reuse requires mode 2 or 4, both saved halfwords to match, length at most 21, descriptor bit 13 clear and bit 4 set. With all predicates true, the original BLX reaches `0x09000010`, passing the word loaded from context+28 (`0x13579BDF`); failing a predicate takes the setup path. Fast-path register writes occur after the optional callback.

**Limits:** The callback is a controlled returning stub, so invocation and argument forwarding are covered, not callback effects. 5C8E, 6140, 6AC0 and 664C are also controlled. Helper side effects, concurrent mutation and physical behavior remain unresolved. No canonical admission is made.
