# P2-21185 independent review

Status: partial / unaccepted. No source or gate changes.

Fresh replay passed for 0x4815F2..0x48162C (58 bytes); instruction and literal-reference outputs match. The frameless leaf accepts only unsigned indices 56..62 and 125..131, computes the bank and normalized 16-byte-stride offset with the -69 term and +112 bank adjustment, then directly stores the full entry R1 word through the 0x4817D8 base. Invalid indices return 6 without a memory write. There is no helper call, source/target read, PRIMASK change, or stack frame in this fragment.
