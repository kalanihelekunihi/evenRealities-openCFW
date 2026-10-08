# P2-20905 independent review

Status: **partial / unaccepted**.

Fresh replay passed for 88 bytes at 0x47D818..0x47D870; image/source hashes and tiling match. The initial 0x4A2FDC result is tested full-width: zero takes diagnostics and does not make a message call; nonzero reaches a second helper whose full-width zero/nonzero branches call different message routines. The helper results are not returned. The POP aliases return SP0 (saved entry R5 unless logger 253 overwrote it), SP4 (saved R6 unless logger literal overwrote it), and saved R7 into R2. No LOW8 guard is used for these helper selections.
