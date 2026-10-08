# P2-21297 independent review

Status: partial / unaccepted. No source or gate changes.

Fresh isolated replay passed for 0x482DD8..0x482E4C (116 bytes); instruction/reference outputs match. The 20-byte no-call frame saves the entry bytes at the recorded offsets. Each of the three output-byte calculations uses the exact observed weighted multiply and `32897 >> 23` scaling, with byte truncation and the recorded per-byte order. SP3 is unwritten before the full-word SP0 load, so the upper result byte remains unspecified. The five-register POP aliasing and final live R0 value match the candidate. No higher-level blend or rounding contract is inferred.
