/* SPDX-License-Identifier: MIT. Independently reconstructed from locked
 * f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5.
 * Kernel mutex419de2/419e22/41a24e and priority/owner helpers. Scheduler
 * helpers are real source dependencies; no timing or cancellation promise. */
#include "mutex_kernel.h"
#include "queue_receive.h"
#include "queue_send.h"
#include "timer_wait.h"
#include <stddef.h>
#define W(a) (*(volatile uint32_t *)(uintptr_t)(a))
#define CURRENT 0x20027134u
#define READY 0x20024870u
#define HIGHEST 0x2002714cu
extern uint32_t opencfw_bl_mask_interrupts(void);
extern void opencfw_bl_kernel_enter(void);
extern void opencfw_bl_kernel_exit(void);
extern void opencfw_bl_scheduler_suspend(void);
extern uint32_t opencfw_bl_scheduler_resume(void);
extern void opencfw_bl_kernel_reschedule(void);
extern uint32_t opencfw_bl_queue_runtime_mode(void);
extern uint32_t opencfw_bl_remove_event_waiter(uint32_t *);
static _Noreturn void fail(void) {
    (void)opencfw_bl_mask_interrupts();W(UINT32_MAX)=0;
    for (;;) __asm__ volatile("b .":::"memory");
}
uint32_t opencfw_boot_current_task(void) {return W(CURRENT);}
uint32_t opencfw_boot_mutex_claim_current(void) {
    uint32_t *t=(uint32_t *)(uintptr_t)W(CURRENT);
    if(t)t[25]++;
    return W(CURRENT);
}
/* Append the task's state item exactly as the stock ready-list insertion.
 * The list index chooses the insertion anchor; no sorting is performed. */
static void ready_insert(uint32_t *t) {
    uint32_t priority=t[11];
    if(W(HIGHEST)<priority)W(HIGHEST)=priority;
    uint32_t *list=(uint32_t *)(uintptr_t)(READY+20*priority);
    uint32_t *anchor=(uint32_t *)(uintptr_t)list[1];
    uint32_t *previous=(uint32_t *)(uintptr_t)anchor[2];
    t[2]=(uint32_t)(uintptr_t)anchor;t[3]=(uint32_t)(uintptr_t)previous;
    previous[1]=(uint32_t)(uintptr_t)(t+1);anchor[2]=(uint32_t)(uintptr_t)(t+1);
    t[5]=(uint32_t)(uintptr_t)list;list[0]++;
}
uint32_t opencfw_boot_mutex_inherit(uint32_t *owner) {
    if(!owner)return 0;
    uint32_t *current=(uint32_t *)(uintptr_t)W(CURRENT);
    uint32_t priority=current[11];
    if(owner[11]>=priority)return owner[24]<priority;
    if(!(owner[6]&0x80000000u))owner[6]=56-priority;
    if(owner[5]==READY+20*owner[11]) {
        (void)opencfw_boot_list_unlink(owner+1);owner[11]=priority;ready_insert(owner);
    } else owner[11]=priority;
    return 1;
}
void opencfw_boot_mutex_disinherit_timeout(uint32_t *owner,uint32_t waiting_priority) {
    if(!owner)return;
    if(!owner[25])fail();
    uint32_t priority=owner[24]>waiting_priority?owner[24]:waiting_priority;
    if(owner[11]==priority || owner[25]!=1)return;
    if((uint32_t)(uintptr_t)owner==W(CURRENT))fail();
    uint32_t old=owner[11];owner[11]=priority;
    if(!(owner[6]&0x80000000u))owner[6]=56-priority;
    if(owner[5]==READY+20*old) {
        (void)opencfw_boot_list_unlink(owner+1);ready_insert(owner);
    }
}
uint32_t opencfw_boot_mutex_waiter_priority(uint32_t *queue) {
    return queue[9]?56-W(queue[12]):0;
}
uint32_t opencfw_bl_kernel_mutex_take_plain(uint32_t *queue,uint32_t ticks) {
    if(!queue || queue[16] || (!opencfw_bl_queue_runtime_mode() && ticks))fail();
    uint32_t state[2],captured=0,inherited=0;
    for(;;) {
        opencfw_bl_kernel_enter();uint32_t count=queue[14];
        if(count) {
            queue[14]=count-1;
            if(!queue[0])queue[2]=opencfw_boot_mutex_claim_current();
            if(queue[4] && opencfw_bl_remove_event_waiter(queue+4))opencfw_bl_kernel_reschedule();
            opencfw_bl_kernel_exit();return 1;
        }
        if(!ticks){opencfw_bl_kernel_exit();return 0;}
        if(!captured){opencfw_boot_timeout_capture(state);captured=1;}
        opencfw_bl_kernel_exit();opencfw_bl_scheduler_suspend();
        opencfw_bl_kernel_enter();volatile int8_t *locks=(volatile int8_t *)queue+0x44;
        if(locks[0]==-1)locks[0]=0;
        if(locks[1]==-1)locks[1]=0;
        opencfw_bl_kernel_exit();
        if(!opencfw_boot_timeout_check(state,&ticks)) {
            if(opencfw_boot_queue_empty(queue)) {
                if(!queue[0]) {
                    opencfw_bl_kernel_enter();
                    inherited=opencfw_boot_mutex_inherit((uint32_t *)(uintptr_t)queue[2]);
                    opencfw_bl_kernel_exit();
                }
                opencfw_boot_wait_list_sorted(queue+9,ticks);
                opencfw_boot_timer_queue_unlock(queue);
                if(!opencfw_bl_scheduler_resume())opencfw_bl_kernel_reschedule();
            } else {
                opencfw_boot_timer_queue_unlock(queue);(void)opencfw_bl_scheduler_resume();
            }
        } else {
            opencfw_boot_timer_queue_unlock(queue);(void)opencfw_bl_scheduler_resume();
            if(!opencfw_boot_queue_empty(queue))continue;
            if(inherited) {
                opencfw_bl_kernel_enter();
                opencfw_boot_mutex_disinherit_timeout((uint32_t *)(uintptr_t)queue[2],opencfw_boot_mutex_waiter_priority(queue));
                opencfw_bl_kernel_exit();
            }
            return 0;
        }
    }
}
uint32_t opencfw_bl_kernel_mutex_take_tagged(uint32_t *queue,uint32_t ticks) {
    if(!queue)fail();
    if(queue[2]==opencfw_boot_current_task()){queue[3]++;return 1;}
    uint32_t result=opencfw_bl_kernel_mutex_take_plain(queue,ticks);
    if(result)queue[3]++;
    return result;
}
uint32_t opencfw_bl_kernel_mutex_give_tagged(uint32_t *queue) {
    if(!queue)fail();
    if(queue[2]!=opencfw_boot_current_task())return 0;
    queue[3]--;
    if(!queue[3])(void)opencfw_bl_kernel_queue_put_blocking(queue,0,0,0);
    return 1;
}
