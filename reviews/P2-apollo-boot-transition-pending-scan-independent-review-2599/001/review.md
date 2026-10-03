# Independent review 2599: transition pending scan

**Result: PASS_SCOPED.** `accepted` remains false.

The candidate receipt and artifact hashes match. The authenticated source image and body `[0x42CFE0, 0x42D0F2)` hashes match. I redirected a copy of the replay to a fresh output directory; all 1,536 cases pass.

Independent Thumb disassembly agrees with the pseudocode. A zero gate exits without a write; index byte 2 writes output 1. Otherwise the code calls `0x41F3F0`, and a nonzero result combined with low mode nibble 1 or 2 writes output 1. The remaining path scans 16 entries at `table + 512 + 32*i`, requiring entry bit 0 and the mask bit for that index. It extracts the 9-bit field from bits 8–16 and accepts `[0,6)`, `[19,25)`, or `[256,480)`, writing 1 on a match or 0 after exhaustion. The epilogue returns saved R7 in R0.

The matrix covers the stated boundary values, shortcut branches, first/last slots, and selected/unselected masks. It uses only one active entry per fixture, with all other entry-valid bits clear. `0x41F3F0` remains controlled; multiple active entries, mutation/concurrency, physical meaning, and enclosing ownership remain outside scope. No canonical admission is claimed.
