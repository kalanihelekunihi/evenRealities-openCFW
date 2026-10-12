# Boot power-transition ambient return correction

Locked stock SHA-256: `f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5`.

Native 0x41b954 begins with `stmdb sp!,{r1,r2,r3,r4,r5,r6,r7,r8,r9,lr}` and ends at 0x41ba7c with `ldmia.w sp!,{r1,r2,r3,r4,r5,r6,r7,r8,r9,pc}`. R1 is restored unchanged from entry on every return. The decompiler's `CONCAT44(local_28,status)` does not model this epilogue correctly. The selected C previously produced only uint32_t status; the new named Thumb entry forwards raw R0/R1 to the selected transition C core, which returns status in R0 and ambient entry R1 as the high word.

The selected `opencfw_boot_control_mode_two` caller consumes only the low status. This change does not infer a value for ambient R1 or alter the authored MMIO/IRQ path. Target compilation and object link pass; runtime equality for all transition/wake cases remains a separate gate.

`boot-coplacement-transition-ambient-round/receipt.json` is terminal `PASS_BOUNDED_LINK`: 373 selected C/ASM units, 1,010 providers, three genuine ROM imports, 34 callback relocations, and a 158,612-byte candidate versus 148,599-byte stock file. This is a source build, not final image equality. Conservative direct-root header-only proof backlog is 180 of 654; whole catalogue has 278 of 903. Indirect roots, final scatter/layout, ROM contracts and physical power behavior remain open.
