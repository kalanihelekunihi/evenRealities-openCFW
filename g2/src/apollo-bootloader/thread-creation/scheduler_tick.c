/* SPDX-License-Identifier: MIT. Stock418408 tick/delay wakeup and timeslice. */
#include <stdint.h>
extern uint32_t opencfw_bl_mask_interrupts(void);
extern void opencfw_boot_next_unblock_refresh(void);
#define WORD(a) (*(volatile uint32_t *)(uintptr_t)(a))
static void remove_item(uint32_t *item) {
    uint32_t *list=(uint32_t *)(uintptr_t)item[4];
    uint32_t *next=(uint32_t *)(uintptr_t)item[1];
    uint32_t *previous=(uint32_t *)(uintptr_t)item[2];
    next[2]=(uintptr_t)previous;previous[1]=(uintptr_t)next;
    if (list[1]==(uintptr_t)item)list[1]=(uintptr_t)previous;
    item[4]=0;list[0]--;
}
uint32_t opencfw_bl_tick_increment(void) {
    uint32_t switch_needed=0;
    if (WORD(0x2002716c)) {WORD(0x20027154)++;return 0;}
    WORD(0x20027148)++;
    uint32_t tick=WORD(0x20027148);
    if (!tick) {
        uint32_t *list=(uint32_t *)(uintptr_t)WORD(0x20027138);
        if (list[0]) {
            (void)opencfw_bl_mask_interrupts();WORD(UINT32_MAX)=0;
            for (;;)__asm__ volatile("b .":::"memory");
        }
        uint32_t old=WORD(0x20027138);WORD(0x20027138)=WORD(0x2002713c);
        WORD(0x2002713c)=old;WORD(0x2002715c)++;
        opencfw_boot_next_unblock_refresh();
    }
    if (tick>=WORD(0x20027164)) {
        for (;;) {
            uint32_t *list=(uint32_t *)(uintptr_t)WORD(0x20027138);
            if (!list[0]) {WORD(0x20027164)=UINT32_MAX;break;}
            uint32_t *first=(uint32_t *)(uintptr_t)list[3];
            uint32_t *tcb=(uint32_t *)(uintptr_t)first[3];
            if (tick<tcb[1]) {WORD(0x20027164)=tcb[1];break;}
            remove_item(tcb+1);
            if (tcb[10])remove_item(tcb+6);
            uint32_t priority=tcb[11];
            if (WORD(0x2002714c)<priority)WORD(0x2002714c)=priority;
            uint32_t *ready=(uint32_t *)(uintptr_t)(0x20024870+20*priority);
            uint32_t *index=(uint32_t *)(uintptr_t)ready[1];
            tcb[2]=(uintptr_t)index;tcb[3]=index[2];
            uint32_t *previous=(uint32_t *)(uintptr_t)index[2];
            previous[1]=(uintptr_t)tcb+4;index[2]=(uintptr_t)tcb+4;
            tcb[5]=(uintptr_t)ready;ready[0]++;
            uint32_t *current=(uint32_t *)(uintptr_t)WORD(0x20027134);
            if (current[11]<priority)switch_needed=1;
        }
    }
    uint32_t *current=(uint32_t *)(uintptr_t)WORD(0x20027134);
    uint32_t *ready=(uint32_t *)(uintptr_t)(0x20024870+20*current[11]);
    if (ready[0]>=2)switch_needed=1;
    if (WORD(0x20027158))switch_needed=1;
    return switch_needed;
}
