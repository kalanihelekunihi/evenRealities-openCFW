# P2-21029 independent review

Status: partial / unaccepted. No source or gate changes.

Fresh replay passed; 40 bytes at 0x47EF10..0x47EF38. The wrapper returns saved R7. The indexed entry rejects full-zero pointer or unsigned index >=34; indices 0..33 produce base+(index<<4), calls a 16-byte copy, then explicitly returns zero; helper result is discarded.
