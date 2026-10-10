.section .text.probe_pneg,"ax",@progbits
.global probe_pneg
probe_pneg:
 pneg.s16.s r0,r0
 rts
