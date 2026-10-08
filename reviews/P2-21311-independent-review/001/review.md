# P2-21311 independent review

Status: partial / unaccepted. No source or gate changes.

Fresh isolated replay passed for 0x483044..0x48306C (40 bytes); instruction/reference outputs match. The 16-byte frame checks a fresh cursor and byte through the ASCII predicate. In the body, the cursor is reloaded and incremented/stored before an independent byte reread at the old address; this ordering can expose a changed value under aliasing. The accumulator update uses wrapping multiply-add by ten. A nondigit returns the current accumulator in R0 and saved entry R3 in R1 via POP. No sign, overflow, length, or null guards are inferred.
