# P2-21151 independent review

Status: partial / unaccepted. No source or gate changes.

Fresh replay passed for 0x480C56..0x480D06 (176 bytes); instruction and literal-reference outputs match. The frameless byte query performs separate fresh word reads in priority order (bit 8, then bit 0). In the 16-byte-frame routine, the output byte at offset 12 is zeroed immediately after the helper call and before checking the full helper result. On the zero-result path, qualification uses successive fresh reads: nibble equality, a second nibble threshold, and SP0<255; a third nibble read controls decrement. Four later output updates are separate and ordered. The continuation and epilogue remain outside this prefix.
