/* SPDX-License-Identifier: MIT. Test-only MPS3 vector/entry wrapper. */
.syntax unified
.thumb
.section .vectors,"a"
.word 0x20080000
.word reset_entry
.word fault_entry
.word fault_entry
.word fault_entry
.word fault_entry
.word fault_entry
.word 0,0,0,0
.word opencfw_boot_svc_entry
.word fault_entry
.word 0
.word opencfw_boot_pendsv_entry
.word fault_entry
.word irq_entry
.text
.global reset_entry
.thumb_func
reset_entry:
 bl harness_main
 b .
.global task_entry
.thumb_func
task_entry:
 push {r12,lr}
 ldr r12,=initial_regs
 stmia r12,{r0-r11}
 pop {r0,r1}
 str r0,[r12,#48]
 str r1,[r12,#52]
 bl task_main
 b .
.global idle_entry
.thumb_func
idle_entry:
 push {r12,lr}
 ldr r12,=initial_regs
 stmia r12,{r0-r11}
 pop {r0,r1}
 str r0,[r12,#48]
 str r1,[r12,#52]
 ldr r0,[r12]
 bl idle_main
 b .
.global irq_entry
.thumb_func
irq_entry:
 mov r1,lr
 mrs r0,psp
 push {r4,lr}
 bl record_irq
 pop {r4,pc}
.global fault_entry
.thumb_func
fault_entry:
 mov r1,lr
 tst lr,#4
 ite eq
 mrseq r0,msp
 mrsne r0,psp
 bl record_fault
 b .
