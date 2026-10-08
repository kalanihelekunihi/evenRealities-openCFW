# P2-21209 independent review

Status: partial / unaccepted. No source or gate changes.

Fresh replay passed for 0x481BB8..0x481C48 (144 bytes); instruction and literal-reference outputs match. The pointer conversion advances the argument cursor, clears the high word, and stores the resulting zero-extended 64-bit value at SP8/SP12; SP72 is stored at SP20 before conversion dispatch. Count policy is checked before argument consumption. On rejection, the code uses ADR 0x4826B4 and the existing diagnostic path. The zero-policy arm dispatches on SP66, including the listed modifier destinations. The `l` and `h` cases each fetch and consume the pointer before null testing; null uses ADR 0x4826CC. The nonnull `h` case writes the low 16 bits of SP52 with STRH. Other modifier handler bodies remain unresolved.
