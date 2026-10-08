# P2-21203 independent review

Status: partial / unaccepted. No source or gate changes.

Fresh replay passed for 0x481A28..0x481A98 (112 bytes); instruction and literal-reference outputs match. The string handler advances the argument cursor by four and stores the fresh argument at SP20; the null case checks byte 1 through the pointer at SP172. A nonzero byte leads to a 4D40A0 call and comparison of the full helper result with 0xFFFFFFFF; only an exact match follows the recorded common path. The separate 482684 loop tests the full return before decrement/retry, with the zero-entry wrap caveat preserved. Prefix emission reloads callback state from SP192 and sends post-incremented bytes with current SP16 state, replacing that state with each full callback result; zero routes to error. Later continuation remains unresolved.
