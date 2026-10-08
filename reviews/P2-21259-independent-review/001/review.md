# P2-21259 independent review

Status: partial / unaccepted. No source or gate changes.

Fresh extraction replay passed for all four disjoint intervals (136 bytes total); the fresh bytes.json matches the candidate exactly. I verified the two post-return zero halfwords, formatter control word and string literals with NUL/padding boundaries, raw four-word float-related pool, callback error strings, null-string fallback bytes, and nan/NAN/inf/INF/zero strings. The intervals align with the reviewed adjacent code boundaries, but no ownership/exhaustiveness claim is made. Raw pool words are retained without interpreting them as executable content or assuming arithmetic semantics.
