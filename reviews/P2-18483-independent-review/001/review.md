# Independent review P2-18483

Status: partial, unaccepted. No source or gate changes.

Fresh GNU replay confirms the exact 44-byte span `0x460424..0x460450`; instruction/reference manifests match. The adapter pushes R1/R2/R3/R4/R5/LR (24 bytes), retains incoming R0 in R4, and passes SP+4 to `0x43C0E4` with the stated first arguments and live R3. Since SP+4 is the saved incoming R2 slot, the callee receives a pointer into the adapter's own frame.

After that call, the adapter writes byte zero at SP4 and the low byte of retained incoming R0 at SP5, then writes full word 4 at SP0. It calls `0x464F76` with R0=3, R1=SP+4, R2=2, R3=0. The last child result is not copied back. POP loads SP0/SP4/SP8 into R0/R1/R2 and restores saved R4/R5/LR. Thus R0 is 4 provided the last child leaves SP0 unchanged; R1 returns the full post-call word at SP4, including any mutation of the two-byte payload and upper bytes. The frame aliasing means the passed buffer can overlap a saved register slot.

The child’s memory effects are unresolved, so neither unconditional return 4 nor preservation of payload-adjacent bytes is claimed. Partial/unaccepted only.
