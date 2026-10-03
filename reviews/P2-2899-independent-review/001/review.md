# Independent review 2899

**PASS_SCOPED**; `accepted` remains false.

The pinned image hash matches inventory. Body [42ADB8,42AE6C) SHA-256 matches the receipt; candidate artifact hashes were checked. Isolated replay of the script into a fresh output directory passed all 192 cases. The cases cross four R0 inputs (low byte 0/1, plus 256/257), four control low-10-bit boundaries, two upper-word patterns, three profile words, and PRIMASK 0/1. The original ADB8 path conditionally sets bits 15–16 at 400201B0, loads profile word104 to update 40020088, chooses delta min(7,1023-control_low10), then updates control low10 while retaining upper bits. The original AE24 call performs its two profile RMWs, then nonzero input subtracts delta from control low10; the combined call sequence returns the observed final control and delta registers, preserves the asserted high registers/SP/PRIMASK, and matches the ordered write ledger. Fixture-controlled state is stable across each helper call; changing volatile reads, aliasing, flags beyond checked outputs, restore-helper behavior, physical MMIO, and caller ownership remain outside this packet. Accepted remains false; no canonical admission.

Candidate receipt SHA-256: `c97f3f39d5a113e3e79dba0c3bd9d4bdaf9f5f76b5402acf3bd14ad171ee6b5a`.
Candidate replay SHA-256: `36653df816d6d0ed63d6fc4d84c319b0c4af7590c148ebf1a4dec4ed3745af79`.
