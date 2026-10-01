# Independent review 1921 — touch row payload copy 1921

**Result: PASS_SCOPED.** Candidate `g2/build/pseudocode-first/20260930T190500Z/analysis/touch-row-payload-copy-814c-1914/002`; receipt SHA-256 `b0d335e5b1974f454d0cd92d84429ee689b57ead6849c3e26fdb9c29a683b1cf`.

Receipt file hashes and source hash match. Body [0x814C,0x81F2) is 166 bytes/78 Thumb instructions; alignment and the three literal words are outside the body. Replayed the immutable script from a unique temporary output directory: all 64 fixtures pass and generated replays.json exactly matches the candidate.

Disassembly supports the distinct primary and mirror paths. The captured width determines quarter-byte offset; mirror displacement is computed from the context halfword and byte fields with 32-bit arithmetic. Provider arguments preserve handle, source offset, length, and destination offset. Primary provider failure returns 0x093E0002 directly; mirror outcomes select success/failure/invalid statuses and flow through blank-row suppression on the advanced mirror row.

The fixture matrix varies both checksum outcomes, mirror selection, callback result, and sequence/checksum blank fields. It initializes headers for both primary and mirror rows, addressing the earlier candidate’s missing mirror-header setup. Controlled checksum/provider callbacks mean these fixtures validate the routine’s decisions given those statuses, not the callback implementations.

Synthetic memory only; physical storage, mutable context, general geometry, concurrency, and canonical admission remain unresolved.
