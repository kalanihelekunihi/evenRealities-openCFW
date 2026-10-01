# Independent review 1777: scoped pass

The exact body is 7E68..7EA4 (60 bytes, 30 instructions). The 21 isolated fixtures reproduce the returned CRC and each byte-read address for lengths through 257. Instruction flow initializes 0xFF and a 16-bit index, XORs each input byte, performs eight high-bit-conditioned shift/XOR rounds with polynomial 0x31, increments the index modulo 65536, compares that index against the full incoming R1, and returns without a final XOR. The pseudocode matches the instruction sequence.

The wrap-related nontermination warning is derived from the index width and full-width comparison; lengths beyond tested fixtures were not run. No canonical acceptance or coverage change is made.
