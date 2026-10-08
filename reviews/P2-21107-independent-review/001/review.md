# P2-21107 independent review

Status: partial / unaccepted. No source or gate changes.

Fresh replay passed for 0x4801FC..0x48028A (142 bytes); instruction/reference outputs match candidate. The frameless initializer preserves the initial low-bit clear before the full-word store, followed by the ordered constant stores and separate bit-30 RMW. It returns the pointer literal in R0 and last written word in R1. The second entry ignores the 4C44BC result, multiplies full R0 by six modulo 2^32, stores it, then performs independent bit-15, bit-1 set/clear, and bit-0 operations. It returns the literal pointer, not the product/status; 8-byte frame teardown restores saved R4. No timing/MMIO semantics inferred.
