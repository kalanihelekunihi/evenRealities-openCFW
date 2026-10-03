# Independent review 2381

**Result:** PASS_SCOPED.

Candidate receipt SHA-256 3fd7e47f588330ab11b95891c6ee13c34330a168e5cd530efed2a4d16b0f2cf3; source SHA-256 371d8a61b659a33b4cad4a7d892e144aba8263ae59497b4f658afc5b0c430f87 matches the pinned value. All five pinned bodies [0x5CA2,0x5CAA), [0x7B14,0x7B62), [0x7B62,0x7B6A), [0x7B6A,0x7BB8), [0x7BB8,0x7BC0) match their recorded byte hashes; evidence-file hashes match.

Independent replay passes all 1,024 combinations: both wrappers, count 0–3, all eight three-row type masks, four child-status patterns, and four descriptor-word patterns. Original wrapper/traversal instructions execute; only child 0x7984 is controlled.

Both traversals freshly read root and its count at each loop test, select only rows matching their complementary type predicate, OR the controlled child statuses, then clear cfg byte 115 and freshly loaded descriptor word 8 bits 4/5. The complete selected-index/argument list, two-write order, returned status, R4-R6 and SP assertions pass. Replay output hash matches candidate replays.json.

**Limits:** Only the supplied three-row synthetic layout and static type/count values are covered; mutation during child calls and aliasing are unresolved. The child 0x7984 behavior is controlled; no child semantics or physical effects are inferred. Null context is not safe under the decoded load path and has no supported contract. Private bounded evidence only; accepted:false.
