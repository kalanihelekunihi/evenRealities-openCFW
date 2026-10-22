/* SPDX-License-Identifier: MIT
 * Native CASE 0xc478 IRQ callback dispatch and 0xcd80 task event send.
 */
#include <stdint.h>
extern void vEventGroupClearBitsCallback(void *event_group,uint32_t bits);
extern uint32_t case_policy_irq_event_dispatch(uint32_t descriptor,uint32_t event,uint32_t bits,uint32_t option); /* 0xce0c */
extern uint32_t case_policy_task_lookup(uint32_t task); /* 0xca4c */
extern uint32_t case_policy_task_message_send(uint32_t scheduler,const uint32_t *args,uint32_t timeout,uint32_t option,uint32_t meta); /* 0xc686 */
extern uint32_t case_policy_task_message_special(uint32_t task,const uint32_t *args,uint32_t option,uint32_t unused,uint32_t meta); /* 0xc7a8 */
uint32_t case_policy_event_irq_apply(uint32_t event,uint32_t bits)
{return case_policy_irq_event_dispatch((uint32_t)(uintptr_t)vEventGroupClearBitsCallback,event,bits,0u);}
/* Native cd80 allocates20 bytes and writes only the first three message
 * words. The configured16-byte queue also copies the untouched fourth
 * stack word. Preserve that source-derived ambient-stack ABI explicitly;
 * a three-word C array would overread, and zero padding would invent data.
 * Calls retain real providers; no opcode array or executable blob. */
/* Stock 0x0800CD80 (case_policy_task_event_send) */
__attribute__((naked,noinline)) uint32_t case_policy_task_event_send(uint32_t task,uint32_t op,uint32_t value,uint32_t option,uint32_t timeout)
{
    __asm__ volatile(
        "push {r4,r5,r6,r7,lr}\n"
        "sub sp, #20\n"
        "ldr r5, [sp, #40]\n"
        "mov r7, r3\n"
        "movs r3, #0\n"
        "cmp r0, #0\n"
        "beq 3f\n"
        "ldr r4, =0x20000164\n"
        "ldr r6, [r4]\n"
        "cmp r6, #0\n"
        "beq 6f\n"
        "str r1, [sp, #0]\n"
        "str r2, [sp, #4]\n"
        "str r0, [sp, #8]\n"
        "cmp r1, #6\n"
        "bge 5f\n"
        "bl case_policy_task_lookup\n"
        "cmp r0, #2\n"
        "beq 4f\n"
        "movs r3, #0\n"
        "mov r2, r3\n"
        "mov r1, sp\n"
        "ldr r0, [r4]\n"
        "bl case_policy_task_message_send\n"
        "mov r3, r0\n"
        "b 6f\n"
        "3: cpsid i\n"
        "2: b 2b\n"
        "4: movs r3, #0\n"
        "mov r2, r5\n"
        "mov r1, sp\n"
        "ldr r0, [r4]\n"
        "bl case_policy_task_message_send\n"
        "mov r3, r0\n"
        "b 6f\n"
        "5: movs r3, #0\n"
        "mov r2, r7\n"
        "mov r1, sp\n"
        "mov r0, r6\n"
        "bl case_policy_task_message_special\n"
        "mov r3, r0\n"
        "6: mov r0, r3\n"
        "add sp, #20\n"
        "pop {r4,r5,r6,r7,pc}\n"
    );
}
