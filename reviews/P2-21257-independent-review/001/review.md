# P2-21257 independent review

Status: partial / unaccepted. No source or gate changes.

Fresh isolated replay passed for 0x482684..0x4826B2 (46 bytes); instruction/reference outputs match. A zero incoming count skips the memory and callback path. Otherwise, each iteration reads and postincrements the source pointer, freshly loads state, calls the callback with live values, and stores the full callback result before testing it. A zero result takes the explicit FFFFFFFF error return without incrementing the state counter. Successful iterations freshly reload and increment the counter, then decrement the full count. Both epilogues use the 24-byte POP sequence, which places saved entry R3 in R1. Callback behavior is not assumed.
