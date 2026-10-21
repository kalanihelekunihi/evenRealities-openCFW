/* SPDX-License-Identifier: MIT
 * Reconstructed local wrappers 41ac44,41ac5a,41f9d8,41f9e6.
 * Public names describe operands, not physically measured delay accuracy.
 * Preserve the original unusual pop-to-r0/r1 return register behavior.
 */
.syntax unified
.thumb
.section .text.opencfw_boot_coprocessor_enable,"ax",%progbits
.global opencfw_boot_coprocessor_enable
.thumb_func
opencfw_boot_coprocessor_enable:
    movw r0,#0xed88
    movt r0,#0xe000
    ldr r1,[r0]
    orr r1,r1,#0x00f00000
    str r1,[r0]
    dsb sy
    isb sy
    bx lr
.section .text.opencfw_boot_fp_lazy_mode,"ax",%progbits
.global opencfw_boot_fp_lazy_mode
.thumb_func
opencfw_boot_fp_lazy_mode:
    push {r2,r3,r4,lr}
    movs r4,r0
    bl opencfw_boot_control_critical_save
    str r0,[sp]
    movw r1,#0xef34
    movt r1,#0xe000
    ldr r0,[r1]
    bic r0,r0,#0xc0000000
    uxtb r4,r4
    cmp r4,#0
    beq 1f
    movs r2,#0xc0000000
    b 2f
1:  movs r2,#0x80000000
2:  orrs r0,r2
    str r0,[r1]
    ldr r0,[sp]
    msr primask,r0
    pop {r0,r1,r4,pc}
.section .text.opencfw_boot_delay_scaled,"ax",%progbits
.global opencfw_boot_delay_scaled
.thumb_func
opencfw_boot_delay_scaled:
    push {r7,lr}
    mov r1,#1000
    muls r0,r1,r0
    bl opencfw_hal_delay_us
    pop {r0,pc}
.section .text.opencfw_boot_delay_raw,"ax",%progbits
.global opencfw_boot_delay_raw
.thumb_func
opencfw_boot_delay_raw:
    push {r7,lr}
    bl opencfw_hal_delay_us
    pop {r0,pc}
.section .note.GNU-stack,"",%progbits
