# P2-21169 independent review

Status: partial / unaccepted. No source or gate changes.

Fresh replay passed for 0x481142..0x481230 (238 bytes); instruction and literal-reference outputs match. Mode 1 ORs a fresh SP0 mask into the first indexed bank word and, only for UXTB selector 2, repeats at the second bank offset +112. Mode 2 contains seven unrolled updates per bank. Each update reads a fresh input mask before reading and clearing its target word. Selector 1 skips the first bank; selector 0 skips the second; other byte values execute both. The second bank uses a new set of input observations, so the sequence is not a bulk copy or a snapshot. Continuation/epilogue remain unresolved.
