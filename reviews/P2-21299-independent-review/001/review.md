# P2-21299 independent review

Status: partial / unaccepted. No source or gate changes.

Fresh isolated replay passed for 0x482E4C..0x482ED4 (136 bytes); instruction/reference outputs match. The 8-byte frame preserves its two input words. Alpha >=253 and alpha <3 shortcuts use the specified fresh reads; intermediate alpha recomputes the alpha byte for each channel and processes offsets 2, 1, 0 using the recorded weighted multiply followed by logical shift 8. The second output high byte is preserved, and all paths release the frame with ADD SP,8 and return via BX LR. No divide-by-255 or rounding semantics are inferred.
