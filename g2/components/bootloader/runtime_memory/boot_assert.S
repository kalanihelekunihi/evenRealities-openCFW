/* SPDX-License-Identifier: MIT */
/* Native Boot assertion reporter, 0x415734 -> 0x417c28 -> 0x41b298.
 * The semihosting BKPT and failure loop are architectural source behavior. */
.syntax unified
.thumb
.section .text.opencfw_boot_assert_report,"ax",%progbits
.global opencfw_boot_assert_report
.type opencfw_boot_assert_report,%function
.thumb_func
opencfw_boot_assert_report:
    push {lr}
    sub sp, #12
    str r1, [sp, #0]
    str r2, [sp, #4]
    str r0, [sp, #8]
    mov r2, sp
    ldr r1, =0x00021010
    movs r0, #24
    bkpt #0xab
    cmp r0, #0
    bne .Lassert_return
    bl opencfw_boot_assert_abort
.Lassert_return:
    add sp, #12
    pop {pc}
.size opencfw_boot_assert_report, .-opencfw_boot_assert_report

.section .text.opencfw_boot_assert_abort,"ax",%progbits
.global opencfw_boot_assert_abort
.type opencfw_boot_assert_abort,%function
.thumb_func
opencfw_boot_assert_abort:
    movs r0, #1
    b opencfw_boot_semihost_exit_loop
.Lassert_unreachable:
    b .Lassert_unreachable
.size opencfw_boot_assert_abort, .-opencfw_boot_assert_abort

.section .text.opencfw_boot_semihost_exit_loop,"ax",%progbits
.global opencfw_boot_semihost_exit_loop
.type opencfw_boot_semihost_exit_loop,%function
.thumb_func
opencfw_boot_semihost_exit_loop:
    push {r7, lr}
    nop.w
    ldr r2, =0x00020026
.Lsemihost_again:
    movs r1, r2
    movs r0, #24
    bkpt #0xab
    b .Lsemihost_again
.size opencfw_boot_semihost_exit_loop, .-opencfw_boot_semihost_exit_loop
