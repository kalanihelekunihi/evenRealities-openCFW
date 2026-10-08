# P2-21255 independent review

Status: partial / unaccepted. No source or gate changes.

Fresh isolated replay passed for 0x48262C..0x482672 (70 bytes); instruction and reference outputs match exactly, including the literal at 0x482680. The 24-byte frame returns the original pair when R4 is zero. Otherwise, bit 0 controls the conditional first helper call; the second helper call runs unconditionally on each iteration, including the final positive iteration. R4 is arithmetic-shifted and tested for zero, so a negative starting R4 remains negative and does not naturally terminate. Helper arithmetic semantics are unresolved.
