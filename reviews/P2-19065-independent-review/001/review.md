# P2-19065 independent review

Status: partial, unaccepted. No source or gate changes.

Fresh isolated replay passed for 0x468E8E–0x468F04 (118 bytes; 49 instructions), using locked image SHA-256 `19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701`. Candidate and fresh instruction/reference records match exactly.

Confirmed selector 74 routes both predicate outcomes to return one without action; selector 8 conditionally calls the child; selector 64 has its diagnostic route and other selectors share the return-one path.

Out-of-range continuations remain unresolved; no broader semantic or corpus-gate claim is made.
