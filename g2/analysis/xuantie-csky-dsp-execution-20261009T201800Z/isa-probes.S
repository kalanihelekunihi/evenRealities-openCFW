.section .text.probe_paddh,"ax",@progbits
.global probe_paddh
probe_paddh:
 paddh.s16 r0,r0,r1
 rts
.section .text.probe_paddsat,"ax",@progbits
.global probe_paddsat
probe_paddsat:
 padd.s16.s r0,r0,r1
 rts
.section .text.probe_pabs,"ax",@progbits
.global probe_pabs
probe_pabs:
 pabs.s16.s r0,r0
 rts
.section .text.probe_pmax,"ax",@progbits
.global probe_pmax
probe_pmax:
 pmax.u16 r0,r0,r1
 rts
.section .text.probe_mulca,"ax",@progbits
.global probe_mulca
probe_mulca:
 mulca.s16.s r0,r0,r1
 rts
.section .text.probe_mulcax,"ax",@progbits
.global probe_mulcax
probe_mulcax:
 mulcax.s16.s r0,r0,r1
 rts
.section .text.probe_mulaca,"ax",@progbits
.global probe_mulaca
probe_mulaca:
 mulaca.s16.s r2, r0, r1
 mov r0,r2
 rts
.section .text.probe_mulacax,"ax",@progbits
.global probe_mulacax
probe_mulacax:
 mulacax.s16.s r2, r0, r1
 mov r0,r2
 rts
