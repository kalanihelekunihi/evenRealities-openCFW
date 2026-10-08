# Dispatch and cleanup literal pool

Partial/unaccepted. Exact 88 bytes at 0x4849A4..0x4849FC, decoded as 22 little-endian words.

- 0x4849A4: 0x2006F690
- 0x4849A8: 0x2006F548
- 0x4849AC: 0x007865F0
- 0x4849B0: 0x0077FBE4
- 0x4849B4: 0x00760A70
- 0x4849B8: 0x0077FBD0
- 0x4849BC: 0x006E859C
- 0x4849C0: 0x0077FC0C
- 0x4849C4: 0x0077FBF8
- 0x4849C8: 0x2006F684
- 0x4849CC: 0x0073F4D0
- 0x4849D0: 0x00760A90
- 0x4849D4: 0x00786620
- 0x4849D8: 0x00786610
- 0x4849DC: 0x00786600
- 0x4849E0: 0x00786630
- 0x4849E4: 0x0077FC20
- 0x4849E8: 0x007780BC
- 0x4849EC: 0x0073F4FC
- 0x4849F0: 0x007780D4
- 0x4849F4: 0x0074A834
- 0x4849F8: 0x00786640

RAM addresses are runtime references; their ownership is unresolved. Consumers are recorded in maps 21818 through 21856. The global at 0x2006F548 supplies list heads and counters; 0x2006F684 supplies the reentrancy guard. Flash pointers used by diagnostics require separate pointed-data recovery. No C implementation, corpus freeze, whole-artifact coverage, or byte-equality claim.
