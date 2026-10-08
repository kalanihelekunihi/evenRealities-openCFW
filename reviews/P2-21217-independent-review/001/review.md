# P2-21217 independent review

Status: partial / unaccepted. No source or gate changes.

Fresh replay passed for 0x481DE8..0x481E46 (94 bytes); instruction and literal-reference outputs match. The 4D4150 call receives the raw pair plus SP, and both returned words are stored back to SP8/SP12. The hex path for conversion `a` writes `0x` or `0X` in order through the pointer at SP20 and increments the SP28 count by two. The special-path entry at 0x481E14 is an ADR to 0x4826F0 followed by a branch to the three-byte-copy path; it does not fall through the normalization island. At 0x481E22 the high word is masked with 0x7FFFFFFF, and IT EQ conditionally tests the low word only if that masked high word was zero. The zero path initializes R6/R5 and branches to 0x4820C0; nonzero routes `a` to hex precision and other conversions to the decimal path. Numeric/helper semantics remain unresolved.
