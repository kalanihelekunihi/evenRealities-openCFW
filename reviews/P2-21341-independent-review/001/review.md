# P2-21341 independent review

Status: partial / unaccepted. No source or gate changes.

Fresh isolated replay passed for 0x48360C..0x483612 (6 bytes); instruction/reference outputs match. The tail adds 48 to SP then pops seven saved registers and PC (32 bytes), releasing the full 80-byte frame. It does not overwrite the output helper's R0-R3 result/effects before return. The following halfword remains excluded as adjacent padding.
