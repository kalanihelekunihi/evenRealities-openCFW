# Independent review 2445

**Result:** PASS_SCOPED.

Audit receipt SHA-256 03ae43e248e1c9bc05eacc9d500a6be5364cf3fdb244daa36535fb77c35e33ba; the pinned source SHA-256 371d8a61b659a33b4cad4a7d892e144aba8263ae59497b4f658afc5b0c430f87 matches. Receipt pins for audit.json, verify.py and notes.md all validate. The 34,432-byte source covers flat interval [0x3300,0xB980).

Independent record verification rehashed all 118 included range records against their referenced receipt hashes and source bytes. The interval union yields 37 unique intervals, 32 merged extents and 5,596 covered bytes. The complement has 33 gaps totaling 28,836 bytes; covered plus gaps equals all 34,432 source bytes. Duplicate/overlapping records are not double-counted.

Isolated verify.py replay reproduces the included record set, interval union and complement exactly when run against the audit's original snapshot (excluding its own later receipt and subsequent audits). A current unfiltered rerun sees the audit's own receipt and newer 2446/2448 receipts as additional unsupported-schema exclusions; the byte partition and 118 included records remain unchanged. The output is an evidence-location map only, not code ownership, execution coverage or completeness.

**Limits:** Schema coverage is narrow: only same-source receipts with paired body_range/body_ranges plus body_sha256 are included. Receipts that identify bodies via code_spans, root_body_range, additional_body_ranges, nested body objects, disassembly address lists, or hash-only ranges are excluded; later 2446 and 2448 audits demonstrate these omitted schemas. Source-matching receipts with malformed/unsupported metadata and mismatched digests are listed as exclusions; receipts for other source hashes are skipped. Gaps may be code, data, padding or evidence represented in unsupported formats. Included bytes may also be literals/data, overlapping candidates or unresolved ownership. No pseudocode completeness, entry ownership, independent acceptance, freeze status or canonical admission follows from this map; accepted:false.
