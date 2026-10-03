# Independent review 2205

**Result:** PASS_SCOPED.

The source and all receipt files match their hashes. The independently sliced wrapper [0x6044, 0x6078) is 52 bytes and matches its body hash; independent Thumb/M-class disassembly agrees with the stored listing.

An isolated replay regenerated all 192 fixtures exactly. Original 6044, 5FC6, both leaf bodies and 4492/449A execute without interception. The replay checks both ordered calls, port/pin/function/mode and fifth stack argument, all four affected words per port, PRIMASK restoration, R4 and SP. The wrapper reloads root/table before each child, reads the first port/pin at table+8/+12 and second at +16/+20, and forwards saved function, mode and stack enable. The second child's incidental R0 is retained. Cases include same-port aliasing and separate ports, with pin 0/7 boundaries.

**Limits:** Root/table contents remain static during these fixtures; mutation and null/fault behavior are untested. Only supplied RAM-backed mappings are covered. Physical MMIO semantics, arbitrary buffers and concurrency remain unresolved. No canonical admission is made.
