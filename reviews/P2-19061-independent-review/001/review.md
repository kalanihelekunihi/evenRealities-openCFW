# P2-19061 independent review

Status: partial, unaccepted. No source or gate changes.

Fresh isolated replay passed for 0x468D96–0x468DFA (100 bytes; 36 instructions), using locked image SHA-256 `19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701`. Candidate and fresh instruction/reference records match exactly.

Confirmed FULL predicate result check is distinct from the fresh byte test, followed by ordered diagnostic reads and return-one branch; no child-result semantics inferred.

Out-of-range continuations remain unresolved; no broader semantic or corpus-gate claim is made.
