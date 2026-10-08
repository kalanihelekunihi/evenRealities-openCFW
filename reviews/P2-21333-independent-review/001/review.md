# P2-21333 independent review

Status: partial / unaccepted. No source or gate changes.

Fresh isolated replay passed for 0x483424..0x48348C (104 bytes); instruction/reference outputs match. Flag bit 10 selects default precision 6 versus retained R7. The zero-fill loop is unsigned, bounded by 32 output bytes, and decrements precision only while it is at least 10. The floating path preserves the exact signed integer conversion, unsigned fractional conversion, indexed eight-byte table load, multiply, and VCMP/VMRS LT condition. Host rounding or full literal-table interpretation is not inferred.
