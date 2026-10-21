/* SPDX-License-Identifier: MIT. Independent M55 assembly reconstruction.
 * SVC41b374/dispatch41b448/first restore41b2ac/PendSV41b31c/FPU41b3ba.
 * Real exception entry/return and FP stack behavior not emulated here.
 */
.syntax unified
.thumb
.text
.global opencfw_boot_svc_entry
.type opencfw_boot_svc_entry,%function
.thumb_func
opencfw_boot_svc_entry:
    tst lr, #4
    ite eq
    mrseq r0, msp
    mrsne r0, psp
    b opencfw_boot_svc_dispatch
.size opencfw_boot_svc_entry,.-opencfw_boot_svc_entry

.global opencfw_boot_svc_dispatch
.type opencfw_boot_svc_dispatch,%function
.thumb_func
opencfw_boot_svc_dispatch:
    push {r7,lr}
    ldr r0, [r0,#24]
    ldrb r0, [r0,#-2]
    uxtb r0,r0
    cmp r0,#2
    bne 1f
    bl opencfw_boot_port_fpu_enable
    bl opencfw_boot_first_task_restore
    pop {r0,pc}
1:  bl opencfw_bl_mask_interrupts
    movs r0,#0
    movs r1,#0
    mvns r1,r1
    str r0,[r1]
2:  b 2b
.size opencfw_boot_svc_dispatch,.-opencfw_boot_svc_dispatch

.global opencfw_boot_first_task_restore
.type opencfw_boot_first_task_restore,%function
.thumb_func
opencfw_boot_first_task_restore:
    ldr r2, =0x20027134
    ldr r1,[r2]
    ldr r0,[r1]
    ldm r0!,{r1,r2}
    msr psplim,r1
    movs r1,#2
    msr control,r1
    adds r0,#32
    msr psp,r0
    isb sy
    mov r0,#0
    msr basepri,r0
    bx r2
.size opencfw_boot_first_task_restore,.-opencfw_boot_first_task_restore

.global opencfw_boot_pendsv_entry
.type opencfw_boot_pendsv_entry,%function
.thumb_func
opencfw_boot_pendsv_entry:
    mrs r0,psp
    tst lr,#16
    it eq
    vstmdbeq r0!,{s16-s31}
    mrs r2,psplim
    mov r3,lr
    stmdb r0!,{r2-r11}
    ldr r2,=0x20027134
    ldr r1,[r2]
    str r0,[r1]
    mov r0,#48
    msr basepri,r0
    dsb sy
    isb sy
    bl opencfw_boot_thread_select
    mov r0,#0
    msr basepri,r0
    ldr r2,=0x20027134
    ldr r1,[r2]
    ldr r0,[r1]
    ldm r0!,{r2-r11}
    tst r3,#16
    it eq
    vldmiaeq r0!,{s16-s31}
    msr psplim,r2
    msr psp,r0
    bx r3
.size opencfw_boot_pendsv_entry,.-opencfw_boot_pendsv_entry

.global opencfw_boot_port_fpu_enable
.type opencfw_boot_port_fpu_enable,%function
.thumb_func
opencfw_boot_port_fpu_enable:
    ldr r0,=0xe000ed88
    ldr r1,[r0]
    orr r1,r1,#0x00f00000
    str r1,[r0]
    ldr r0,=0xe000ef34
    ldr r1,[r0]
    orr r1,r1,#0xc0000000
    str r1,[r0]
    bx lr
.size opencfw_boot_port_fpu_enable,.-opencfw_boot_port_fpu_enable
