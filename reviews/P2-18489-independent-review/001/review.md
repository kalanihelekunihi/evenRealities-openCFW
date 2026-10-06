# Independent review P2-18489

Status: partial, unaccepted. No source or gate changes.

Fresh GNU replay confirms the exact 92-byte span `0x460524..0x460580`; instruction and PC-reference manifests match. The routine inherits the 80-byte frame (48 local bytes plus 32 saved bytes). On the zero result from `0x490C32`, it calls `0x43D0CE`, tests bit 1, and on that path writes the literal at SP4 and 327 at SP0 before calling `0x43D574`. These are local frame slots, not the saved-register slots. Further mask checks use separate fresh `0x43D0CE` calls; the bit-2 path calls `0x43CE9E`, while the other route sets R0=0 and joins the epilogue.

The nonzero `0x490C32` route loads a halfword from SP+20, retains the second buffer pointer in R2, and calls `0x475B14` with R0=1/R1=3. Both zero and nonzero child results join the same exit; the full child R0 is retained as the routine result. The epilogue adds 52 to SP, discarding 48 locals plus the saved R3 word, then restores R4-R9 and PC. R0 is not restored from the stack. The halfword at SP+20 derives from earlier stack state, without assuming it is a fixed value.

Children remain semantically unresolved; no retry or larger routine behavior is claimed. Partial/unaccepted only.
