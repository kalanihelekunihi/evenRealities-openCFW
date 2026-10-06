/* SPDX-License-Identifier: MIT. Original41a114..41a24e receive, timeout
 * 418912/418922, sorted wait41863e, empty41a5c4, copy41a52c, dynamic419d08.
 * Event wake is an explicit dependency; no synthetic scheduling is hidden here. */
#include "queue_receive.h"
#include "timer_wait.h"
#include <stddef.h>
#define WORD(a) (*(volatile uint32_t *)(uintptr_t)(a))
extern uint32_t opencfw_bl_mask_interrupts(void);
extern void opencfw_bl_kernel_enter(void);
extern void opencfw_bl_kernel_exit(void);
extern void opencfw_bl_scheduler_suspend(void);
extern uint32_t opencfw_bl_scheduler_resume(void);
extern void opencfw_bl_kernel_reschedule(void);
extern uint32_t opencfw_bl_queue_runtime_mode(void);
extern uint32_t opencfw_bl_remove_event_waiter(uint32_t *);
extern uintptr_t opencfw_bl_rtos_allocate(uint32_t);
extern void opencfw_boot_list_initialize(uint32_t *);
static void fail(void) {
    (void)opencfw_bl_mask_interrupts();WORD(UINT32_MAX)=0;
    for (;;) __asm__ volatile("b .":::"memory");
}
void opencfw_boot_timeout_capture(uint32_t state[2]) {
    state[0]=WORD(0x2002715c);state[1]=WORD(0x20027148);
}
uint32_t opencfw_boot_timeout_check(uint32_t state[2],uint32_t *remaining) {
    if (!state || !remaining)fail();
    opencfw_bl_kernel_enter();uint32_t now=WORD(0x20027148);
    uint32_t elapsed=now-state[1],expired;
    if (*remaining==UINT32_MAX)expired=0;
    else if (WORD(0x2002715c)!=state[0] && now>=state[1]) {*remaining=0;expired=1;}
    else if (elapsed<*remaining) {*remaining-=elapsed;opencfw_boot_timeout_capture(state);expired=0;}
    else {*remaining=0;expired=1;}
    opencfw_bl_kernel_exit();return expired;
}
void opencfw_boot_wait_list_sorted(uint32_t *list,uint32_t ticks) {
    if (!list)fail();
    uint32_t *current=(uint32_t *)(uintptr_t)WORD(0x20027134);
    opencfw_boot_list_insert_sorted(list,current+6);opencfw_boot_task_block(ticks,1);
}
uint32_t opencfw_boot_queue_empty(uint32_t *queue) {
    opencfw_bl_kernel_enter();uint32_t empty=queue[14]==0;opencfw_bl_kernel_exit();return empty;
}
void opencfw_boot_queue_copy_out(uint32_t *queue,void *message) {
    uint32_t size=queue[16];
    if (size) {
        uint32_t next=queue[3]+size;
        if (next>=queue[2])next=queue[0];queue[3]=next;
        const volatile uint8_t *from=(const volatile uint8_t *)(uintptr_t)next;
        volatile uint8_t *to=(volatile uint8_t *)message;
        for (uint32_t i=0;i<size;i++)to[i]=from[i];
    }
}
uint32_t opencfw_bl_kernel_queue_get_blocking(uint32_t *queue,void *message,uint32_t timeout) {
    if (!queue || (!message && queue[16]))fail();
    if (!opencfw_bl_queue_runtime_mode() && timeout)fail();
    uint32_t state[2],captured=0;
    for (;;) {
        opencfw_bl_kernel_enter();uint32_t count=queue[14];
        if (count) {
            opencfw_boot_queue_copy_out(queue,message);queue[14]=count-1;
            if (queue[4] && opencfw_bl_remove_event_waiter(queue+4))opencfw_bl_kernel_reschedule();
            opencfw_bl_kernel_exit();return 1;
        }
        if (!timeout) {opencfw_bl_kernel_exit();return 0;}
        if (!captured) {opencfw_boot_timeout_capture(state);captured=1;}
        opencfw_bl_kernel_exit();opencfw_bl_scheduler_suspend();
        volatile int8_t *locks=(volatile int8_t *)queue+0x44;
        opencfw_bl_kernel_enter();
        if (locks[0]==-1)locks[0]=0;
        if (locks[1]==-1)locks[1]=0;
        opencfw_bl_kernel_exit();
        if (!opencfw_boot_timeout_check(state,&timeout)) {
            if (opencfw_boot_queue_empty(queue)) {
                opencfw_boot_wait_list_sorted(queue+9,timeout);
                opencfw_boot_timer_queue_unlock(queue);
                if (!opencfw_bl_scheduler_resume())opencfw_bl_kernel_reschedule();
            } else {
                opencfw_boot_timer_queue_unlock(queue);(void)opencfw_bl_scheduler_resume();
            }
        } else {
            opencfw_boot_timer_queue_unlock(queue);(void)opencfw_bl_scheduler_resume();
            if (opencfw_boot_queue_empty(queue))return 0;
        }
    }
}
uintptr_t opencfw_bl_kernel_queue_create_dynamic(uint32_t count,uint32_t item_size,uint32_t type) {
    if (!count || UINT32_MAX/count<item_size)fail();
    uint32_t bytes=count*item_size;
    if (bytes>=UINT32_MAX-79)fail();
    uintptr_t cb=opencfw_bl_rtos_allocate(bytes+80);
    if (!cb)return 0;
    uint32_t *q=(uint32_t *)cb;volatile uint8_t *raw=(volatile uint8_t *)q;
    raw[0x46]=0;q[0]=item_size?cb+80:cb;q[15]=count;q[16]=item_size;
    opencfw_bl_kernel_enter();
    q[2]=q[0]+bytes;q[14]=0;q[1]=q[0];q[3]=q[0]+(count-1)*item_size;
    raw[0x44]=255;raw[0x45]=255;
    opencfw_boot_list_initialize(q+4);opencfw_boot_list_initialize(q+9);
    opencfw_bl_kernel_exit();raw[0x4c]=(uint8_t)type;return cb;
}
