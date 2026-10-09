/* SPDX-License-Identifier: MIT. Recovered main-image456110/456210/456280/4562da; algorithm adapted from preserved bootloader helper, all main bindings independently checked.
 * RTOS heap is separate from TLSF wrapper41fd70. Exact ARM32 field arithmetic.
 */
#include <stdint.h>
extern void stock_scheduler_suspend(void);
extern uint32_t stock_scheduler_resume(void);
extern void audio_heap_malloc_failed(void);
extern uint32_t audio_heap_mask_interrupts(void);
#define WORD(a) (*(volatile uint32_t *)(uintptr_t)(a))
#define NEXT(p) WORD(p)
#define SIZE(p) WORD((p)+4)
#define START 0x20074158u
#define END WORD(0x2007465c)
#define FREE WORD(0x20074660)
#define MINFREE WORD(0x20074664)
static void audio_heap_assert_failure(void) {
    (void)audio_heap_mask_interrupts();WORD(UINT32_MAX)=0;
    for (;;)__asm__ volatile("b .":::"memory");
}
void audio_main_heap_initialize(void) {
    uint32_t base=0x20004558,total=0x2f000;
    uint32_t begin=(base+7)&~7u;total-=begin-base;
    NEXT(START)=begin;SIZE(START)=0;
    END=(begin+total-8)&~7u;NEXT(END)=0;SIZE(END)=0;
    SIZE(begin)=END-begin;NEXT(begin)=END;
    FREE=MINFREE=SIZE(begin);
}
void audio_main_heap_insert(uint32_t block) {
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
void *pvPortMalloc(uint32_t bytes) {
    uint32_t result=0,n=bytes;
    stock_scheduler_suspend();
    if (!END)audio_main_heap_initialize();
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
                uint32_t split=block+n;if (split&7)audio_heap_assert_failure();
                SIZE(split)=SIZE(block)-n;SIZE(block)=n;
                audio_main_heap_insert(split);
            }
            FREE-=SIZE(block);if (FREE<MINFREE)MINFREE=FREE;
            SIZE(block)|=0x80000000;NEXT(block)=0;WORD(0x20074668)++;
        }
    }
    (void)stock_scheduler_resume();
    if (!result)audio_heap_malloc_failed();
    if (result&7)audio_heap_assert_failure();return (void *)(uintptr_t)result;
}
void vPortFree(void *memory) {
    if (!memory)return;
    uint32_t block=(uint32_t)(uintptr_t)memory-8;
    if (!(SIZE(block)&0x80000000) || NEXT(block))audio_heap_assert_failure();
    SIZE(block)&=~0x80000000;
    stock_scheduler_suspend();FREE+=SIZE(block);
    audio_main_heap_insert(block);WORD(0x2007466c)++;
    (void)stock_scheduler_resume();
}
