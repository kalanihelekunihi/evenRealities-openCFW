# P2-21111 independent review

Status: partial / unaccepted. No source or gate changes.

Fresh replay passed for 0x480312..0x480358 (70 bytes); instruction/reference outputs match candidate. The three wrappers use table offsets +4, +12, and +16. Each performs a nonnull test and later independent callback reload; mutable table contents could therefore differ between the guard and call. Only the first wrapper narrows entry R0/R1 to LOW8 call arguments; other wrappers pass the callback address/table pointer and live R2/R3 as decoded. Null callback routes return zero without initializing output storage. Callback results return full R0. The second/third wrappers use POP R1,PC, restoring saved R7 into R1. No callback behavior inferred.
