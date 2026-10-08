# P2-21035 independent review

Status: partial / unaccepted. No source or gate changes.

Fresh replay passed for 0x47EFCC..0x47F0A0 (212 bytes); fresh instructions and references match the candidate. The 20-iteration counter guard is checked before each bit-2 read and delay call, so no read follows the twentieth delay. F018 cleanup and the 4803DC call apply only on the mode-two route; the other route bypasses them. Both poll loops update low state bits using fresh word reads. At the common status tail, the low-byte mode/status conditions select distinct SP0/SP1 byte writes, mutating the saved entry R1 slot. Final PRIMASK restore loads from SP4 and R0 returns R4. Stack aliases and helper writes are preserved; no timing or MMIO claims are made.
