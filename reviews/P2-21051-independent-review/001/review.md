# P2-21051 independent review

Status: partial / unaccepted. No source or gate changes.

Fresh replay passed for 0x47F5F6..0x47F6F2 (252 bytes); instruction and reference outputs match candidate. Continuing the inherited 40-byte frame, the record pointer and SP16 are loaded independently where used. The shifted-SP8 condition retains 32-bit wrap semantics and LOW8 index comparison; the separate SP8 mask check controls its own callback. The protected mask update reads SP4 pointer, then reloads it for the store, preserving possible changes between observations, and restores PRIMASK from SP20. Two SP16 reads feed distinct helper arguments. Special cases 20, 23, and 29 retain their separate helper calls and exits. Common teardown frees 28 then pops R4/R5/PC. No external helper or pointed-record semantics inferred.
