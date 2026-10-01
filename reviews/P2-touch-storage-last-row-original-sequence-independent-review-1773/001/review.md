# Independent review 1773: scoped pass

The candidate body is 7FA4..8054 (176 bytes, 84 instructions), with the separate 7FA0 leaf independently decoded as LDR word [R0+4]; BX LR. The 192 isolated fixtures reproduce exact selected pointers, validation calls, status returns, SP and stop PC. The fixture model includes first-pass/second-pass scanning; the pointer continues after the first scan rather than restarting at the base. Only 7F7C validation is substituted.

The scan and row data are synthetic, and 7F7C remains controlled. No canonical acceptance or coverage change is made.
