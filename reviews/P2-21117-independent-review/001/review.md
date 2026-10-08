# P2-21117 independent review

Status: partial / unaccepted. No source or gate changes.

Fresh replay passed for 0x480434..0x4804AA (118-byte prefix); instruction/reference outputs match candidate. The 16-byte frame and callback-table helper arguments are explicit; no memset behavior is assumed from the call. Version V and state S observations are fresh on every occurrence and short-circuit in the mapped order. The second predicate is evaluated after the first flag-byte store, so alias effects remain possible. Comparisons preserve unsigned semantics. The prefix ends at 4804AA with frame active; no return or complete-table initialization claim.
