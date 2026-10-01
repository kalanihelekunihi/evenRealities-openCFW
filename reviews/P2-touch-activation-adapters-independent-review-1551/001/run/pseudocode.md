# Activation adapters

5CA2 [5CA2,5CAA) and 7BB8 [7BB8,7BC0) preserve incoming arguments, call 7B62 and 7B6A respectively, forward the raw R0 result and restore an eight-byte frame.

5C7A [5C7A,5C8E) returns 1 for null incoming R0. Otherwise it calls 5C72 with R0=0, R1=5, R2=the incoming pointer and R3 unchanged; it forwards the raw result. It restores an eight-byte frame on both paths.

5C8E [5C8E,5C98) loads pointer at incoming R0+4, reads its word+8, and returns that word & 0x80. This is a raw mask result, either 0 or 128; there is no frame or helper.

5C02 [5C02,5C1E) takes index in R0 and descriptor in R1. Select record at descriptor word+12 + 144*index; if record byte123 is 7, return the unchanged incoming index without calling a helper. Otherwise call 5BC0 with original R0/R1, scratch R2=123 and R3=record byte123 and return its raw result. Restore the eight-byte frame.

46 original-instruction fixtures check null handling, all three row indices, exact byte gating, status masks, raw return propagation, helper argument registers and stack restoration. Deeper callees remain controlled; no physical or whole-firmware claim is made. No canonical admission or C implementation.
