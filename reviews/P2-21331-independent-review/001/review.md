# P2-21331 independent review

Status: partial / unaccepted. No source or gate changes.

Fresh isolated replay passed for 0x4833A6..0x483424 (126 bytes); instruction/reference outputs match. The special comparison's EQ/NE and bit-2 branches select separate ordered stack tuples. The fallback path compares d0 against the fifth argument and a second literal, retaining the recorded GE/PL/MI conditions and live entry arguments. The sign/magnitude tail uses a separate eight-byte literal compare and conditionally applies VNEG to d0. Literal references are only four-byte prefixes; payload meanings and special-value labels remain unasserted.
