# P2-21195 independent review

Status: partial / unaccepted. No source or gate changes.

Fresh replay passed for 0x481884..0x48191E (154 bytes); instruction and literal-reference outputs match. The flag scanner preincrements the format pointer and ORs the observed flag bits. Star width advances the argument cursor by four, stores the signed width, and for negative values performs 32-bit negation (so INT_MIN remains 0x80000000) and sets the left-alignment flag. The non-star parser initializes width to zero, consumes every digit, and only updates while signed width is below the literal limit; the arithmetic wraps modulo 2^32 and clobbers R4 as recorded. A fresh post-loop byte selects dot precision or the absent-precision value 0xFFFFFFFF. Later precision handling and cleanup remain unresolved.
