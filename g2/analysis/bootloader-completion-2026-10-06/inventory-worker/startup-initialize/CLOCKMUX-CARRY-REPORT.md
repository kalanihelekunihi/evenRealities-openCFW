# Clock-mux entry carry reconstruction

Locked image SHA256 f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5, Thumb little-endian, load410000. Original body41acb2..41b04c (922B).

Original entry pushes{r1,r2,r3,r4,r5,r6,r7,r8,r9,lr}; epilogue pops{r0,r1,r2,r4,r5,r6,r7,r8,r9,pc}. SavedR1 andR2 also form liveGPIO/pin stack locals. Therefore returnedR0/R1 contain post-body local values, not merely preserved incoming values; returnedR2 is incomingR3. Original initialization of the GPIO word clears all four bytes before setting low byte1, rather than preserving an ambient high byte.

`clockmux_entry.S` capturesR1/R2/R5 in a12-byte explicit mutable carry structure before entering reconstructedC, copies its finalGPIO/pin words to return slots, and preserves incomingR3 plus ABI callee-saved registers. This is source assembly describing a wrapper, not an opcode payload. `clockmux_entry.h` exposes the explicit C interface and warns that the register-ABI entry is not a normal no-argument C call.

[896-case comparison](clockmux-entry-comparison.json) PASS against original instructions: guard and marker branches, incomingR1/R2/R5, pin reads, child-mutatedGPIO bytes, ordered/finalMMIO, R0/R1/R2, R4..R11, SP andPRIMASK. The same ten child contracts as the previous leaf suite remain controlled. R3/R12/condition flags are outside the defined comparison; physical clocks, delay, IRQ andGPIO hardware are not modeled. Source machine loads only compiled source ELF.

Two earlier mismatches exposed pin-slot return aliasing and full-word GPIO initialization. Both source assumptions were corrected before this PASS result. The earlier failure artifact is superseded, not evidence of current PASS for the old assumptions.

At root41c4b4, if cache flag200271a8 is0, original41c606 loadsR5=20027064; if cache flag is already1, the incomingR5 survives that skipped path. A whole root initializer C replacement must propagate this explicit carry and preserve relevant child register effects; the wrapper by itself does not close the root.

This work is a prerequisite, not linked into promotedc6a3 or preserved validated75ee. Their lineage is [documented separately](../../integrated-status/STARTUP-CHECKPOINT-LINEAGE.md).
