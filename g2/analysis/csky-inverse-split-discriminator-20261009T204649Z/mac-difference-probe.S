.section .text.probe_mulacsx,"ax",@progbits
.global probe_mulacsx
probe_mulacsx:
 mulacsx.s16.s r2,r0,r1
 mov r0,r2
 rts
