/* SPDX-License-Identifier: MIT
 * Native 0x422698 / 0x4226cc. These are flag-returning binary64 compare
 * helpers: operands occupy r0:r1 and r2:r3, and callers inspect APSR.
 * They do not return an ordinary C scalar. Keep exact named ISA operations.
 */
.syntax unified
.thumb
.text

.global opencfw_boot_double_cmp_flags_lr
.type opencfw_boot_double_cmp_flags_lr,%function
.thumb_func
opencfw_boot_double_cmp_flags_lr:
    orr.w ip, r1, r3
    orrs.w ip, r0, ip, lsl #1
    orrs.w ip, r2, ip
    mov.w ip, #0x200000
    bcc 1f
    beq 2f
    cmn.w ip, r1, lsl #1
    itt ls
    cmnls.w ip, r3, lsl #1
    cmpls r3, r1
    it eq
    cmpeq r2, r0
2:  bx lr
1:  cmn.w ip, r3, lsl #1
    bhi 2b
    cmp r1, r3
    it eq
    cmpeq r0, r2
    bx lr
.size opencfw_boot_double_cmp_flags_lr, .-opencfw_boot_double_cmp_flags_lr

.global opencfw_boot_double_cmp_flags_rl
.type opencfw_boot_double_cmp_flags_rl,%function
.thumb_func
opencfw_boot_double_cmp_flags_rl:
    orr.w ip, r1, r3
    orrs.w ip, r0, ip, lsl #1
    orrs.w ip, r2, ip
    mov.w ip, #0x200000
    bcc 3f
    beq 4f
    cmn.w ip, r1, lsl #1
    itt ls
    cmnls.w ip, r3, lsl #1
    cmpls r1, r3
    it eq
    cmpeq r0, r2
4:  bx lr
3:  cmn.w ip, r1, lsl #1
    bhi 4b
    cmp r3, r1
    it eq
    cmpeq r2, r0
    bx lr
.size opencfw_boot_double_cmp_flags_rl, .-opencfw_boot_double_cmp_flags_rl
