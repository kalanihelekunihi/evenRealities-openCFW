# Independent review 2447

**Result:** PASS_SCOPED.

Receipt SHA-256 dc5ff08dca7d9c635708d905a400da5080ea889d4c2426b041264ea30e260d71; all declared audit/verifier/notes hashes validate. The 34,432-byte pinned image hash 371d8a61b659a33b4cad4a7d892e144aba8263ae59497b4f658afc5b0c430f87 matches the stated source hash and interval [0x3300,0xB980).

Independent verifier replay reproduces the recorded snapshot exactly when excluding its own receipt and later 2448 hash-only audit receipt: 544 matching source receipts, 239 verified extent records, 106 unique intervals, 43 merged extents and 9,436 covered bytes. The 44-gap complement totals 24,996 bytes; extent plus gaps equals the full 34,432-byte image. Every record retains its metadata field and referenced receipt hash; extents are rehashed against source bytes.

This improves over the narrower 2444 audit by validating explicit body/range/code/root-body/additional-body/literal pair fields and `ranges` dictionaries. `ranges` entries deliberately remain semantically unclassified. Duplicate and overlapping extent records are unioned only for location arithmetic. A current unfiltered rerun sees the later 2448 audit as an extra source-matching receipt; the verified extents and partition remain unchanged.

**Limits:** Still excluded: hash-only range lists tied to disassembly, instruction-address spans without paired range hashes, prose/replay-only bounds, and unsupported schema variants. The 2448 packet supplies one such hash-only schema example; 2450-style prose-bracketed bounds are another potential evidence source, not established by this audit. Literal/body categories, entry ownership, incompatible overlapping candidates, and whether gaps are code/data/padding remain unresolved. No executable coverage, completeness, independent acceptance or freeze conclusion follows. Private evidence-location map only; accepted:false and no canonical admission.
