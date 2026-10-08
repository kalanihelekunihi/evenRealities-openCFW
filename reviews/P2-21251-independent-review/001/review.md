# P2-21251 independent review

Status: partial / unaccepted. No source or gate changes.

Fresh isolated replay passed for 0x482518..0x482590 (120 bytes), and instruction/reference outputs match. The 40-byte frame and radix dispatch are consistent with the code. For signed decimal conversions, the high-word sign test gates the exact RSBS/SBC pair negation; the pair-zero check and separate word/byte reads control the zero-prefix path. Octal prefix output is conditional on the fresh byte flag. The entry conversion byte is stored at SP0, overwriting a saved slot, before the 47CC60 call receives the live pair/radix arguments. Helper behavior and continuation remain unresolved.
