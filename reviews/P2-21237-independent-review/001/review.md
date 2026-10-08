# P2-21237 independent review

Status: partial / unaccepted. No source or gate changes.

Fresh isolated replay passed for 0x482200..0x482286 (134 bytes); instruction and reference outputs match the candidate. Fallthrough stores the wrapping R8-R6 difference, while direct entry at 0x482206 bypasses it. The marker and sign outputs follow the recorded branch sequence; R5 is narrowed by SXTH for loop tests and signed division by 10, with quotient/remainder arithmetic preserving the observed modulo operations. The digit loop stores low-order digits into the temporary buffer with postincrement and emits them in reverse by decrementing the count before each fresh indexed byte read. The special `e` minimum-digit path emits zero for count zero or at most one as described. Final pointer difference uses fresh SP20/SP32 reads and stores at SP36; SP32 remains unchanged. Continuation at 0x48231A and external helper behavior are unresolved.
