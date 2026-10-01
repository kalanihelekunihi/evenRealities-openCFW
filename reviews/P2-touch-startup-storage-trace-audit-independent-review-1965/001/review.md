# Independent review 1965 — startup storage trace audit

**Result: PASS_SCOPED.** Candidate `touch-startup-storage-trace-audit-1956/001`; receipt SHA-256 `8c031cd5e8424262d8973d743c92c69e40159ec897f3c94659e23f628e52959b`.

Parent receipt and all pinned files match the audit’s recorded hashes; the audit JSON pin matches. Independently recounted every listed PC from the parent replay’s full 7,384,880-entry trace, and all 25 address counts match exactly. The parent’s four observed public-call records and arguments match the audit.

The decoded calls correspond to 8A38, 8A78, 8AE0, and 8AAC in that order. Stop PC is 3D50 and PRIMASK is zero. Counts include 18 entries at 4810 and 90 entries at 8BF4; these are trace-derived totals for this one fixture, not whole-image totals.

This audit is an independently reproducible trace summary and does not add instruction ownership or coverage claims.

The parent run uses synthetic clock/status reads and explicit modeled interrupt delivery; storage status and flash are synthetic. No physical effects or whole-image coverage are established, and canonical admission remains false.
