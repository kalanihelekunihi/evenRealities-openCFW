# Independent review 15983

Partial, accepted:false. Fresh decode replay passed for 22 bytes. Pushes R5-R7/LR, overwrites saved R5/R6 slots with FFFFFFFF and zero, calls 4B06C0 with entry R0/R1 and synthesized R2=0/R3=1, then pops those stack words into R0/R1/R2 and saved LR into PC. Child R0 is discarded; R2 comes from preserved saved R7 slot.

Child/global/hardware effects remain unqualified; no admission or gate change.
