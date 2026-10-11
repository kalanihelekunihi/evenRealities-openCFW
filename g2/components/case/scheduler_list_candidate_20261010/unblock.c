#include "list_abi.h"

#define CASE_STATE ((volatile uint32_t *)(uintptr_t)0x20000128u)
#define CASE_READY_BASE ((uintptr_t)0x20000ff4u)

/* Original 0x0800c1cc. Caller holds a suspended scheduler and passes a
 * linked event item whose owner is a live TCB with a linked state item. */
void case_unblock_waiter(case_item *event_item,uint32_t event_bits)
{
    if(CASE_STATE[12]==0u){
        __asm volatile("cpsid i" ::: "memory");
        for(;;)__asm volatile("");
    }
    event_item->value=event_bits|0x80000000u;
    case_tcb *task=(case_tcb *)event_item->owner;
    if(!task){
        __asm volatile("cpsid i" ::: "memory");
        for(;;)__asm volatile("");
    }
    case_source_list_remove(event_item);
    case_source_list_remove(&task->state_item);
    uint32_t priority=task->priority;
    if(CASE_STATE[4]<priority)CASE_STATE[4]=priority;
    case_source_list_insert_end((case_list *)(CASE_READY_BASE+priority*20u),&task->state_item);
    if(((case_tcb *)(uintptr_t)CASE_STATE[0])->priority<priority)CASE_STATE[7]=1u;
}
