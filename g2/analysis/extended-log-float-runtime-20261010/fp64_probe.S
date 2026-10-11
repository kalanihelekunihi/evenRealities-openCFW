.syntax unified
.cpu cortex-m55
.fpu fpv5-d16
.thumb

.section .vectors,"a",%progbits
.word 0x20010000
.word reset + 1

.section .text,"ax",%progbits
.global reset
.thumb_func
reset:
    ldr r0, =0xe000ed88
    ldr r1, [r0]
    ldr r2, =0x00f00000
    orrs r1, r2
    str r1, [r0]
    dsb
    isb
    ldr r0, =0x00000000
    ldr r1, =0x3ff80000
    vmov d0, r0, r1
    vmul.f64 d0, d0, d0
    vmov r2, r3, d0
    ldr r0, =0x40020000
    cmp r2, #0
    bne fail
    cmp r3, r0
    bne fail
    movs r0, #4
    ldr r1, =pass_text
    bkpt #0xab
    b stop
fail:
    movs r0, #4
    ldr r1, =fail_text
    bkpt #0xab
stop:
    movs r0, #0x18
    ldr r1, =0x20026
    bkpt #0xab
    b stop

pass_text: .asciz "M55 FP64 PASS\n"
fail_text: .asciz "M55 FP64 FAIL\n"
