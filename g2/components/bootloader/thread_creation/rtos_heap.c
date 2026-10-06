/* SPDX-License-Identifier: MIT. Stock419730/419830/4198a0/4198fa.
 * RTOS heap is separate from TLSF wrapper41fd70. Exact ARM32 field arithmetic.
 */
#include <stdint.h>
extern void opencfw_bl_scheduler_suspend(void);
extern uint32_t opencfw_bl_scheduler_resume(void);
extern void opencfw_bl_malloc_failed(void);
extern uint32_t opencfw_bl_mask_interrupts(void);
#define WORD(a) (*(volatile uint32_t *)(uintptr_t)(a))
#define NEXT(p) WORD(p)
#define SIZE(p) WORD((p)+4)
#define START 0x20027020u
#define END WORD(0x20027108)
#define FREE WORD(0x2002710c)
#define MINFREE WORD(0x20027110)
static void fail(void) {
    (void)opencfw_bl_mask_interrupts();WORD(UINT32_MAX)=0;
    for (;;)__asm__ volatile("b .":::"memory");
}
void opencfw_boot_rtos_heap_initialize(void) {
    uint32_t base=0x2000055c,total=0x14000;
    uint32_t begin=(base+7)&~7u;total-=begin-base;
    NEXT(START)=begin;SIZE(START)=0;
    END=(begin+total-8)&~7u;NEXT(END)=0;SIZE(END)=0;
    SIZE(begin)=END-begin;NEXT(begin)=END;
    FREE=MINFREE=SIZE(begin);
}
void opencfw_boot_rtos_heap_insert(uint32_t block) {
    uint32_t previous=START;
    while (NEXT(previous)<block)previous=NEXT(previous);
    if (previous+SIZE(previous)==block) {
        SIZE(previous)+=SIZE(block);block=previous;
    }
    if (block+SIZE(block)==NEXT(previous)) {
        if (NEXT(previous)!=END) {
            SIZE(block)+=SIZE(NEXT(previous));NEXT(block)=NEXT(NEXT(previous));
        } else NEXT(block)=END;
    } else NEXT(block)=NEXT(previous);
    if (previous!=block)NEXT(previous)=block;
}
uintptr_t opencfw_bl_rtos_allocate(uint32_t bytes) {
    uint32_t result=0,n=bytes;
    opencfw_bl_scheduler_suspend();
    if (!END)opencfw_boot_rtos_heap_initialize();
    if (n) {
        uint32_t add=16-(n&7);
        n=(UINT32_MAX-add<n)?0:n+add;
    }
    if (!(n&0x80000000) && n && n<=FREE) {
        uint32_t previous=START,block=NEXT(START);
        while (SIZE(block)<n && NEXT(block)) {previous=block;block=NEXT(block);}
        if (block!=END) {
            result=NEXT(previous)+8;NEXT(previous)=NEXT(block);
            if (SIZE(block)-n>16) {
                uint32_t split=block+n;if (split&7)fail();
                SIZE(split)=SIZE(block)-n;SIZE(block)=n;
                opencfw_boot_rtos_heap_insert(split);
            }
            FREE-=SIZE(block);if (FREE<MINFREE)MINFREE=FREE;
            SIZE(block)|=0x80000000;NEXT(block)=0;WORD(0x20027114)++;
        }
    }
    (void)opencfw_bl_scheduler_resume();
    if (!result)opencfw_bl_malloc_failed();
    if (result&7)fail();return result;
}
void opencfw_bl_rtos_free(uintptr_t memory) {
    if (!memory)return;
    uint32_t block=(uint32_t)memory-8;
    if (!(SIZE(block)&0x80000000) || NEXT(block))fail();
    SIZE(block)&=~0x80000000;
    opencfw_bl_scheduler_suspend();FREE+=SIZE(block);
    opencfw_boot_rtos_heap_insert(block);WORD(0x20027118)++;
    (void)opencfw_bl_scheduler_resume();
}
