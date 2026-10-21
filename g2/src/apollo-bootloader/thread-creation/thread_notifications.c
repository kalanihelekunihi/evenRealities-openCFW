/* SPDX-License-Identifier: MIT. Stock418dac/418e70 thread-context notification
 * wait/notify and418d7a event wait-result accessor. Only index0 is supported
 * by these actual functions; nonzero indices trigger the stock fatal store.
 * ISR notify418fe8 remains separate, not synthesized by this source. */
#include "thread_notifications.h"
#include "timer_wait.h"
#include <stddef.h>
#define WORD(a) (*(volatile uint32_t *)(uintptr_t)(a))
extern uint32_t opencfw_bl_mask_interrupts(void);
extern void opencfw_bl_kernel_enter(void);
extern void opencfw_bl_kernel_exit(void);
extern void opencfw_bl_kernel_reschedule(void);
extern void opencfw_boot_next_unblock_refresh(void);
static void fail(void) {
    (void)opencfw_bl_mask_interrupts();WORD(UINT32_MAX)=0;
    for (;;) __asm__ volatile("b .":::"memory");
}
uint32_t opencfw_boot_thread_notify_wait(uint32_t index,uint32_t clear_entry,uint32_t clear_exit,uint32_t *output,uint32_t ticks) {
    if (index)fail();
    opencfw_bl_kernel_enter();
    volatile uint32_t *thread=(volatile uint32_t *)(uintptr_t)WORD(0x20027134);
    volatile uint8_t *state=(volatile uint8_t *)thread+0x6c;
    if (*state!=2) {
        thread[26]&=~clear_entry;*state=1;
        if (ticks) {opencfw_boot_task_block(ticks,1);opencfw_bl_kernel_reschedule();}
    }
    opencfw_bl_kernel_exit();opencfw_bl_kernel_enter();
    thread=(volatile uint32_t *)(uintptr_t)WORD(0x20027134);state=(volatile uint8_t *)thread+0x6c;
    if (output)*output=thread[26];
    uint32_t received=*state==2;
    if (received)thread[26]&=~clear_exit;
    *state=0;opencfw_bl_kernel_exit();return received;
}
uint32_t opencfw_boot_thread_notify(uint32_t *thread,uint32_t index,uint32_t value,uint32_t action,uint32_t *previous) {
    if (index || !thread)fail();
    opencfw_bl_kernel_enter();
    if (previous)*previous=thread[26];
    uint8_t *state=(uint8_t *)thread+0x6c;uint32_t old=*state;*state=2;
    uint32_t result=1;
    switch ((uint8_t)action) {
    case 0:break;
    case 1:thread[26]|=value;break;
    case 2:thread[26]++;break;
    case 3:thread[26]=value;break;
    case 4:if (old!=2)thread[26]=value;else result=0;break;
    default:if (WORD(0x20027148))fail();break;
    }
    if (old==1) {
        (void)opencfw_boot_list_unlink(thread+1);
        uint32_t priority=thread[11];
        if (WORD(0x2002714c)<priority)WORD(0x2002714c)=priority;
        uint32_t *list=(uint32_t *)(uintptr_t)(0x20024870+priority*20);
        uint32_t *index_node=(uint32_t *)(uintptr_t)list[1];
        uint32_t *previous_node=(uint32_t *)(uintptr_t)index_node[2];
        thread[2]=(uintptr_t)index_node;thread[3]=(uintptr_t)previous_node;
        previous_node[1]=(uintptr_t)thread+4;index_node[2]=(uintptr_t)thread+4;
        thread[5]=(uintptr_t)list;list[0]++;
        if (thread[10])fail();
        opencfw_boot_next_unblock_refresh();
        uint32_t *current=(uint32_t *)(uintptr_t)WORD(0x20027134);
        if (current[11]<priority)opencfw_bl_kernel_reschedule();
    }
    opencfw_bl_kernel_exit();return result;
}
uint32_t opencfw_boot_thread_wait_result_take(void) {
    uint32_t *thread=(uint32_t *)(uintptr_t)WORD(0x20027134);
    uint32_t result=thread[6];thread[6]=56-thread[11];return result;
}
