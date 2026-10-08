# Independent review — P2-21469

Status: partial; accepted: false.

Fresh replay passed for the exact 102-byte span, and regenerated instruction/reference records match the candidate. Within the open 32-byte frame, the object helper calls and their offsets occur in the listed order. Each 439BE4 call copies three bytes from an object field into SP0, after which the caller reads a full 32-bit word from SP0 and forwards it to 4D48AA or 4D4A2E. Thus the fourth byte is retained memory state, not freshly written by that three-byte copy; this review does not assume its value.

The final parameter path freshly reads object+28 into R1 for 4D4A48(object+64,R1,...). The 32-byte frame remains open, and byte+40 selection lies beyond this slice. Helper memory effects and contracts are unresolved.
