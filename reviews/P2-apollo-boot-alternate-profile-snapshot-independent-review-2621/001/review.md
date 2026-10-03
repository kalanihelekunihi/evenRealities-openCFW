# Independent review 2621: alternate-profile snapshot

**Result: PASS_SCOPED.** `accepted` remains false.

Artifact, source, body, and literal-pointer hashes match. An isolated replay copy with a fresh output directory passes all 45 cases. The branch uses revision low byte 33 with a nonzero full subrevision, or rereads revision and accepts low byte at least 34. The `0x121` case correctly follows the low-byte-33 path.

Disassembly confirms the six snapshot byte stores and their order: source bits 25–29, 11–15, 8–12, 17–21, then a fresh source read for bits 25–29 and 11–15. The fallback values are 14/31/21/31/11/11. Return zero and SP assertions pass.

All source words share one repeated pattern within a fixture, so independent per-register variation and aliasing are not tested. Stable memory, physical meaning, concurrency, and ownership remain unresolved. No canonical admission is claimed.
