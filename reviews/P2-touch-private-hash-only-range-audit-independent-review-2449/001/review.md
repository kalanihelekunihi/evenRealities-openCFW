# Independent review 2449

**Result:** PASS_SCOPED.

Candidate: `g2/build/pseudocode-first/20260930T190500Z/analysis/touch-private-hash-only-range-audit-2448/001`. Receipt SHA-256 `5195d8d4f857a5eba02708a7324f5ce596991636cdfe86cce883a918f1d533cd`; pinned audit, verifier, and notes hashes match the receipt. The source image hash `371d8a61b659a33b4cad4a7d892e144aba8263ae59497b4f658afc5b0c430f87` matches the pinned 34,432-byte image and interval `[0x3300,0xB980)`.

I independently replayed `verify.py` into `/tmp/2449-snapshot-c`, excluding the audit's own receipt and later source-matching receipts 2450, 2452, 2454, and 2456 so the replay uses the candidate's receipt snapshot. The generated audit matches the frozen `audit.json` exactly: 545 matching receipts, 282 verified extent records, 120 unique intervals, 45 merged intervals, and 11,868 covered bytes. The 46 complement gaps total 22,564 bytes, and covered plus gap bytes equal the full image. The verifier rehashes each accepted extent and records the originating receipt path/hash and metadata field.

The hash-only fallback is implemented narrowly: it requires a pinned disassembly file, strictly increasing unique parsed addresses, a Thumb decode whose instruction addresses exactly match that list without gaps, and a digest match over the entire decoded candidate span. This supports 43 `hash_only_disassembly_bounds` records in this snapshot. It does not convert those spans into ownership or control-flow closure claims.

**Limits:** This remains an evidence-location audit, not executable coverage, semantic completeness, entry ownership, or admission. It intentionally omits prose/replay-only boundaries and unsupported schemas; the 373 excluded entries are reported as lacking supported verified extent metadata. Extent category meanings and overlaps remain unresolved, and complement bytes may be code, data, padding, or unrepresented evidence. No canonical records or firmware sources were changed; accepted:false.
