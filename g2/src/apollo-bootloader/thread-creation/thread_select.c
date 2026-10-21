/* SPDX-License-Identifier: MIT. Stock418570 ready selection/history update. */
#include <stdint.h>
extern uint32_t opencfw_bl_mask_interrupts(void);
extern void opencfw_bl_stack_overflow(uint32_t *tcb,const char *name);
#define WORD(a) (*(volatile uint32_t *)(uintptr_t)(a))
void opencfw_boot_thread_select(void) {
    if (WORD(0x2002716c)) {WORD(0x20027158)=1;return;}
    WORD(0x20027158)=0;
    uint32_t *current=(uint32_t *)(uintptr_t)WORD(0x20027134);
    uint32_t *stack=(uint32_t *)(uintptr_t)current[12];
    if (stack[0]!=0xa5a5a5a5 || stack[1]!=0xa5a5a5a5 ||
        stack[2]!=0xa5a5a5a5 || stack[3]!=0xa5a5a5a5)
        opencfw_bl_stack_overflow(current,(const char *)current+0x34);
    uint32_t index=WORD(0x20027170);
    uint32_t *history=(uint32_t *)(uintptr_t)(0x20026500+index*8);
    history[0]=current[22];
    uint32_t priority=WORD(0x2002714c);
    uint32_t *list;
    for (;;) {
        list=(uint32_t *)(uintptr_t)(0x20024870+priority*20);
        if (list[0])break;
        if (!priority) {
            (void)opencfw_bl_mask_interrupts();WORD(UINT32_MAX)=0;
            for (;;)__asm__ volatile("b .":::"memory");
        }
        priority--;
    }
    uint32_t *node=(uint32_t *)(uintptr_t)list[1];
    list[1]=node[1];
    if (list[1]==(uintptr_t)list+8) {
        node=(uint32_t *)(uintptr_t)list[1];list[1]=node[1];
    }
    node=(uint32_t *)(uintptr_t)list[1];
    WORD(0x20027134)=node[3];WORD(0x2002714c)=priority;
    current=(uint32_t *)(uintptr_t)WORD(0x20027134);history[1]=current[22];
    WORD(0x20027170)++;
    if (WORD(0x20027170)>=64)WORD(0x20027170)=0;
}
