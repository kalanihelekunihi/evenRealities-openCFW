# P2-21005 independent review

Status: partial / unaccepted. No source or gate changes.

Fresh replay passed for 0x47EAF6..0x47EB6C (118 bytes); instruction and reference outputs match candidate. The two object accessors are separate 8-byte-frame entries with fatal null paths and distinct fresh field reads: byte 40 bit 0 versus full word 28. The third entry forwards a stack message with SP0=-2 and entry arguments in ordered slots, calls the helper with the fresh global pointer, discards the message area, and returns the helper's full R0. No object or queue ownership semantics inferred.
