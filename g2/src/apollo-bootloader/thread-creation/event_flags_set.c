/* SPDX-License-Identifier: MIT. Stock4164da/419978/4199bc flags creation,
 * 41652e/419af4/419b06 set/read and418838 unordered event waiter unblocking.
 * ISR419bd2 remains a declared dependency. No modeled scheduling in source. */
#include "event_flags_set.h"
#include "timer_wait.h"
#include <stddef.h>
#define WORD(a) (*(volatile uint32_t *)(uintptr_t)(a))
extern uint32_t opencfw_bl_context_guard(void);
extern uint32_t opencfw_bl_mask_interrupts(void);
extern void opencfw_bl_restore_interrupts(uint32_t);
extern uintptr_t opencfw_bl_rtos_allocate(uint32_t);
extern void opencfw_boot_list_initialize(uint32_t *);
extern void opencfw_bl_scheduler_suspend(void);
extern uint32_t opencfw_bl_scheduler_resume(void);
extern void opencfw_boot_next_unblock_refresh(void);
extern uint32_t opencfw_bl_event_flags_set_isr(uint32_t *,uint32_t,uint32_t *);
static void fail(void) {
    (void)opencfw_bl_mask_interrupts();WORD(UINT32_MAX)=0;
    for (;;) __asm__ volatile("b .":::"memory");
}
uintptr_t opencfw_provider_4164da(const uint32_t *attributes) {
    if (opencfw_bl_context_guard())return 0;
    uintptr_t cb=0;uint8_t is_static=0;
    if (attributes && attributes[2] && attributes[3]>=32) {cb=attributes[2];is_static=1;}
    else if (!attributes || (!attributes[2] && !attributes[3]))cb=opencfw_bl_rtos_allocate(32);
    else return 0;
    if (cb) {
        uint32_t *event=(uint32_t *)cb;event[0]=0;opencfw_boot_list_initialize(event+1);
        ((volatile uint8_t *)event)[0x1c]=is_static;
    }
    return cb;
}
uint32_t opencfw_boot_event_flags_read(uint32_t *event) {
    uint32_t previous=opencfw_bl_mask_interrupts();uint32_t flags=*event;
    opencfw_bl_restore_interrupts(previous);return flags;
}
void opencfw_boot_event_wait_unblock(uint32_t *item,uint32_t result) {
    if (!WORD(0x2002716c))fail();
    item[0]=result|0x80000000;
    uint32_t *thread=(uint32_t *)(uintptr_t)item[3];
    if (!thread)fail();
    (void)opencfw_boot_list_unlink(item);opencfw_boot_next_unblock_refresh();
    (void)opencfw_boot_list_unlink(thread+1);
    uint32_t priority=thread[11];
    if (WORD(0x2002714c)<priority)WORD(0x2002714c)=priority;
    uint32_t *list=(uint32_t *)(uintptr_t)(0x20024870+priority*20);
    uint32_t *index=(uint32_t *)(uintptr_t)list[1];
    uint32_t *previous=(uint32_t *)(uintptr_t)index[2];
    thread[2]=(uintptr_t)index;thread[3]=(uintptr_t)previous;
    previous[1]=(uintptr_t)thread+4;index[2]=(uintptr_t)thread+4;
    thread[5]=(uintptr_t)list;list[0]++;
    uint32_t *current=(uint32_t *)(uintptr_t)WORD(0x20027134);
    if (current[11]<priority)WORD(0x20027158)=1;
}
uint32_t opencfw_boot_event_flags_set(uint32_t *event,uint32_t flags) {
    if (!event || (flags&0xff000000))fail();
    uint32_t *list=event+1;uint32_t *end=list+2;uint32_t clear=0;
    opencfw_bl_scheduler_suspend();
    uint32_t *item=(uint32_t *)(uintptr_t)list[3];*event|=flags;
    while (item!=end) {
        uint32_t *next=(uint32_t *)(uintptr_t)item[1];
        uint32_t mask=item[0]&0x00ffffff,control=item[0]&0xff000000;
        uint32_t satisfied=(control&0x04000000)?((*event&mask)==mask):((*event&mask)!=0);
        if (satisfied) {
            if (control&0x01000000)clear|=mask;
            opencfw_boot_event_wait_unblock(item,*event|0x02000000);
        }
        item=next;
    }
    *event&=~clear;(void)opencfw_bl_scheduler_resume();return *event;
}
uint32_t opencfw_provider_41652e(uint32_t *event,uint32_t flags) {
    if (!event || (flags&0xff000000))return 0xfffffffc;
    if (!opencfw_bl_context_guard())return opencfw_boot_event_flags_set(event,flags);
    uint32_t woken=0;
    if (!opencfw_bl_event_flags_set_isr(event,flags,&woken))return 0xfffffffd;
    uint32_t result=opencfw_boot_event_flags_read(event)|flags;
    if (woken)WORD(0xe000ed04)=0x10000000;
    return result;
}
