/* SPDX-License-Identifier: MIT. Source reconstruction of initial timer blocking
 * and its full helper branches. Unrecovered timer expiration/command/rollover
 * and event wake helpers remain declared dependencies, never guessed bodies.
 * 419444/419458/4194be/4194e2,41a5fe/41a556,4186dc/419186,41b572/41b5a8. */
#include "timer_wait.h"
#include <stddef.h>
#define WORD(a) (*(volatile uint32_t *)(uintptr_t)(a))
extern void opencfw_bl_kernel_enter(void);
extern void opencfw_bl_kernel_exit(void);
extern void opencfw_bl_scheduler_suspend(void);
extern uint32_t opencfw_bl_scheduler_resume(void);
extern void opencfw_bl_kernel_reschedule(void);
extern uint32_t opencfw_bl_mask_interrupts(void);
extern uint32_t opencfw_bl_remove_event_waiter(uint32_t *list);
extern void opencfw_bl_missed_yield(void);
extern void opencfw_bl_timer_expire(uint32_t expiry,uint32_t now);
extern void opencfw_bl_timer_rollover(void);
extern void opencfw_bl_timer_process_commands(void);
static void fail(void) {
    (void)opencfw_bl_mask_interrupts();WORD(UINT32_MAX)=0;
    for (;;) __asm__ volatile("b .":::"memory");
}
void opencfw_boot_list_insert_sorted(uint32_t *list,uint32_t *item) {
    uint32_t *before;
    if (item[0]==UINT32_MAX)before=(uint32_t *)(uintptr_t)list[4];
    else {
        before=list+2;
        while (item[0]>=*(uint32_t *)(uintptr_t)before[1])
            before=(uint32_t *)(uintptr_t)before[1];
    }
    uint32_t *next=(uint32_t *)(uintptr_t)before[1];
    item[1]=(uintptr_t)next;next[2]=(uintptr_t)item;
    item[2]=(uintptr_t)before;before[1]=(uintptr_t)item;
    item[4]=(uintptr_t)list;list[0]++;
}
uint32_t opencfw_boot_list_unlink(uint32_t *item) {
    uint32_t *list=(uint32_t *)(uintptr_t)item[4];
    uint32_t *next=(uint32_t *)(uintptr_t)item[1];
    uint32_t *previous=(uint32_t *)(uintptr_t)item[2];
    next[2]=(uintptr_t)previous;previous[1]=(uintptr_t)next;
    if (list[1]==(uintptr_t)item)list[1]=(uintptr_t)previous;
    item[4]=0;list[0]--;return list[0];
}
void opencfw_boot_task_block(uint32_t ticks,uint32_t indefinite) {
    uint32_t now=WORD(0x20027148);
    uint32_t *current=(uint32_t *)(uintptr_t)WORD(0x20027134);
    (void)opencfw_boot_list_unlink(current+1);
    if (ticks==UINT32_MAX && indefinite) {
        uint32_t *list=(uint32_t *)(uintptr_t)0x20026f84;
        uint32_t *index=(uint32_t *)(uintptr_t)list[1];
        uint32_t *previous=(uint32_t *)(uintptr_t)index[2];
        current[2]=(uintptr_t)index;current[3]=(uintptr_t)previous;
        previous[1]=(uintptr_t)current+4;index[2]=(uintptr_t)current+4;
        current[5]=(uintptr_t)list;list[0]++;
    } else {
        uint32_t expiry=now+ticks;current[1]=expiry;
        uint32_t *list=(uint32_t *)(uintptr_t)WORD(expiry<now?0x2002713c:0x20027138);
        opencfw_boot_list_insert_sorted(list,current+1);
        if (expiry>=now && expiry<WORD(0x20027164))WORD(0x20027164)=expiry;
    }
}
void opencfw_boot_wait_list_append(uint32_t *list,uint32_t ticks,uint32_t indefinite) {
    if (!list)fail();
    uint32_t *current=(uint32_t *)(uintptr_t)WORD(0x20027134);
    uint32_t *index=(uint32_t *)(uintptr_t)list[1];
    uint32_t *previous=(uint32_t *)(uintptr_t)index[2];
    current[7]=(uintptr_t)index;current[8]=(uintptr_t)previous;
    previous[1]=(uintptr_t)current+24;index[2]=(uintptr_t)current+24;
    current[10]=(uintptr_t)list;list[0]++;
    opencfw_boot_task_block(indefinite?UINT32_MAX:ticks,indefinite);
}
void opencfw_boot_timer_queue_unlock(uint32_t *queue) {
    volatile int8_t *locks=(volatile int8_t *)queue+0x44;
    opencfw_bl_kernel_enter();
    int8_t transmit=locks[1];
    while (transmit>=1 && queue[9]) {
        if (opencfw_bl_remove_event_waiter(queue+9))opencfw_bl_missed_yield();
        transmit--;
    }
    locks[1]=-1;opencfw_bl_kernel_exit();
    opencfw_bl_kernel_enter();
    int8_t receive=locks[0];
    while (receive>=1 && queue[4]) {
        if (opencfw_bl_remove_event_waiter(queue+4))opencfw_bl_missed_yield();
        receive--;
    }
    locks[0]=-1;opencfw_bl_kernel_exit();
}
void opencfw_boot_timer_queue_wait(uint32_t *queue,uint32_t ticks,uint32_t indefinite) {
    volatile int8_t *locks=(volatile int8_t *)queue+0x44;
    opencfw_bl_kernel_enter();
    if (locks[0]==-1)locks[0]=0;
    if (locks[1]==-1)locks[1]=0;
    opencfw_bl_kernel_exit();
    if (!queue[14])opencfw_boot_wait_list_append(queue+9,ticks,indefinite);
    opencfw_boot_timer_queue_unlock(queue);
}
uint32_t opencfw_boot_tick_get(void) {return WORD(0x20027148);}
uint32_t opencfw_boot_timer_next_expiry(uint32_t *empty) {
    uint32_t *list=(uint32_t *)(uintptr_t)WORD(0x20027178);
    *empty=list[0]?0:1;
    if (*empty)return 0;
    return *(uint32_t *)(uintptr_t)list[3];
}
uint32_t opencfw_boot_timer_sample_time(uint32_t *wrapped) {
    uint32_t now=opencfw_boot_tick_get();
    if (now<WORD(0x20027188)) {opencfw_bl_timer_rollover();*wrapped=1;}
    else *wrapped=0;
    WORD(0x20027188)=now;return now;
}
void opencfw_boot_timer_wait_expiry(uint32_t expiry,uint32_t empty) {
    opencfw_bl_scheduler_suspend();uint32_t wrapped;
    uint32_t now=opencfw_boot_timer_sample_time(&wrapped);
    if (wrapped) {(void)opencfw_bl_scheduler_resume();return;}
    if (!empty && now>=expiry) {
        (void)opencfw_bl_scheduler_resume();opencfw_bl_timer_expire(expiry,now);return;
    }
    if (empty) {
        uint32_t *other=(uint32_t *)(uintptr_t)WORD(0x2002717c);
        empty=other[0]?0:1;
    }
    opencfw_boot_timer_queue_wait((uint32_t *)(uintptr_t)WORD(0x20027180),expiry-now,empty);
    if (!opencfw_bl_scheduler_resume())opencfw_bl_kernel_reschedule();
}
void opencfw_boot_timer_task(void *argument) {
    (void)argument;
    for (;;) {
        uint32_t empty;uint32_t expiry=opencfw_boot_timer_next_expiry(&empty);
        opencfw_boot_timer_wait_expiry(expiry,empty);
        opencfw_bl_timer_process_commands();
    }
}
