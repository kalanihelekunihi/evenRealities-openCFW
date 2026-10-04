# P2-9065 independent scoped review

Status: PASS_SCOPED; accepted: false; status: partial.

- All 64 mapped instruction bytes and the literal global reference match the pinned image.
- The routine computes the slot from low8(index)&15, ORs the full input mask into the selected byte (stored low8), ORs 4 into global byte+60, then unlocks and invokes the wake helper. It returns saved entry R3 through POP-to-R0.

Limitations:

- No slot bounds issue is implied by the low-nibble mask, but index and mask truncation are part of the observed behavior. Gate and wake child contracts/physical delivery are not proven.
