/* Experimental FreeRTOS task ready insertion, stock 0x4549fc. */
#include <stdint.h>
#include "../../foundation/freertos_ready/ready.h"
extern void stock_enter_critical(void);
extern void stock_exit_critical(void);
extern void audio_yield(void);
extern void g2_thread_initialize_lists(void); /* stock 0x45568c */
static volatile uint32_t *const task_count=(volatile uint32_t *)(uintptr_t)0x20074a30u;
static TCB_t *volatile *const current=(TCB_t *volatile *)(uintptr_t)0x20074a20u;
static volatile uint32_t *const task_number=(volatile uint32_t *)(uintptr_t)0x20074a4cu;
static volatile uint32_t *const top_priority=(volatile uint32_t *)(uintptr_t)0x20074a38u;
static volatile uint32_t *const running=(volatile uint32_t *)(uintptr_t)0x20074a3cu;
static List_t *const ready=(List_t *)(uintptr_t)0x2006a49cu;
void g2_thread_schedule_tcb(void *raw) {
    TCB_t *tcb=(TCB_t *)raw;
    stock_enter_critical();
    *task_count=*task_count+1u;
    if(*current==0) {
        *current=tcb;
        if(*task_count==1u) g2_thread_initialize_lists();
    } else if(*running==0u && (*current)->uxPriority<=tcb->uxPriority) {
        *current=tcb;
    }
    *task_number=*task_number+1u;
    *(volatile uint32_t *)((uintptr_t)tcb+0x58u)=*task_number;
    if(*top_priority<tcb->uxPriority) *top_priority=tcb->uxPriority;
    vListInsertEnd(&ready[tcb->uxPriority],&tcb->xStateListItem);
    stock_exit_critical();
    if(*running!=0u && (*current)->uxPriority<tcb->uxPriority) audio_yield();
}
