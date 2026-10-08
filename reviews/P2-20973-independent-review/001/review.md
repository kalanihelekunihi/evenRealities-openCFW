# P2-20973 independent review

Status: partial / unaccepted. No source or gate changes.

Fresh locked replay passed in isolated output for the 54-byte interval 0x47E470..0x47E4A6. Instruction and literal-reference outputs match the candidate.

The comparison uses the LOW8 helper result against a separate fresh byte read from saved SP0. Equality skips both subsequent calls and writes. On mismatch, the helper receives the address of the saved full entry word, then the state word is set and a further helper receives a fresh global word. The shifted POP returns the current SP0 word, so it starts as full entry R0 but can be changed by the address-taking call or callee writes; no equivalence between saved full entry and the separate byte observation is assumed.
