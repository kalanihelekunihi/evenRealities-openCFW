# P2-20831 independent review

Status: **partial / unaccepted**.

Fresh replay passed for 44 instruction bytes; pinned image and source receipt hashes match. The helper rounds via wrapping (entry R2+3) then logical shift right two, forwards live entry arguments to 0x473940, then calls 0x4D0A2C with explicit rounded-count/state arguments and restores PRIMASK from that result. The epilogue POP includes R0 from saved SP0, so the visible return is original entry R3, not the helper result. The body has no stack writes. No CRC-wrapper or interrupt-state contract is inferred.
