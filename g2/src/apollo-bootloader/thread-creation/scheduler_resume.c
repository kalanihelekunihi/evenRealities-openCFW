/* SPDX-License-Identifier: MIT. Stock4181d8/418228/418b28.
 * Tick processing418408 remains explicit provider until independently recovered.
 */
#include <stdint.h>
extern void opencfw_bl_kernel_enter(void);
extern void opencfw_bl_kernel_exit(void);
extern void opencfw_bl_kernel_reschedule(void);
extern uint32_t opencfw_bl_mask_interrupts(void);
extern uint32_t opencfw_bl_tick_increment(void);
#define WORD(a) (*(volatile uint32_t *)(uintptr_t)(a))
void opencfw_bl_scheduler_suspend(void) {WORD(0x2002716c)++;}
void opencfw_boot_next_unblock_refresh(void) {
    uint32_t *list=(uint32_t *)(uintptr_t)WORD(0x20027138);
    if (!list[0])WORD(0x20027164)=UINT32_MAX;
    else {uint32_t *first=(uint32_t *)(uintptr_t)list[3];WORD(0x20027164)=first[0];}
}
static void remove_item(uint32_t *item) {
    uint32_t *container=(uint32_t *)(uintptr_t)item[4];
    uint32_t *next=(uint32_t *)(uintptr_t)item[1];
    uint32_t *previous=(uint32_t *)(uintptr_t)item[2];
    next[2]=(uintptr_t)previous;previous[1]=(uintptr_t)next;
    if (container[1]==(uintptr_t)item)container[1]=(uintptr_t)previous;
    item[4]=0;container[0]--;
}
uint32_t opencfw_bl_scheduler_resume(void) {
    uint32_t switched=0;uintptr_t moved=0;
    if (!WORD(0x2002716c)) {
        (void)opencfw_bl_mask_interrupts();WORD(UINT32_MAX)=0;
        for (;;)__asm__ volatile("b .":::"memory");
    }
    opencfw_bl_kernel_enter();WORD(0x2002716c)--;
    if (!WORD(0x2002716c) && WORD(0x20027144)) {
        uint32_t *pending=(uint32_t *)(uintptr_t)0x20026f5c;
        while (pending[0]) {
            uint32_t *first=(uint32_t *)(uintptr_t)pending[3];
            uint32_t *tcb=(uint32_t *)(uintptr_t)first[3];moved=(uintptr_t)tcb;
            remove_item(tcb+6);remove_item(tcb+1);
            uint32_t priority=tcb[11];
            if (WORD(0x2002714c)<priority)WORD(0x2002714c)=priority;
            uint32_t *list=(uint32_t *)(uintptr_t)(0x20024870+20*priority);
            uint32_t *index=(uint32_t *)(uintptr_t)list[1];
            tcb[2]=(uintptr_t)index;tcb[3]=index[2];
            uint32_t *previous=(uint32_t *)(uintptr_t)index[2];
            previous[1]=(uintptr_t)tcb+4;index[2]=(uintptr_t)tcb+4;
            tcb[5]=(uintptr_t)list;list[0]++;
            uint32_t *current=(uint32_t *)(uintptr_t)WORD(0x20027134);
            if (priority>=current[11])WORD(0x20027158)=1;
        }
        if (moved)opencfw_boot_next_unblock_refresh();
        uint32_t ticks=WORD(0x20027154);
        if (ticks) {
            do {if (opencfw_bl_tick_increment())WORD(0x20027158)=1;} while (--ticks);
            WORD(0x20027154)=0;
        }
        if (WORD(0x20027158)) {switched=1;opencfw_bl_kernel_reschedule();}
    }
    opencfw_bl_kernel_exit();return switched;
}
