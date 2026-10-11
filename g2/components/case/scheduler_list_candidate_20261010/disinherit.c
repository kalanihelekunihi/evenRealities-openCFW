#include "list_abi.h"

#define CASE_STATE ((volatile uint32_t *)(uintptr_t)0x20000128u)
#define CASE_READY_BASE ((uintptr_t)0x20000ff4u)

/* Original 0x0800cb38: mutex holder is either null or the current task.
 * The caller supplies a live TCB with coherent ready-list membership. */
int32_t case_disinherit(case_tcb *holder)
{
    if(!holder)return 0;
    if((uintptr_t)holder!=CASE_STATE[0]){
        __asm volatile("cpsid i" ::: "memory");
        for(;;)__asm volatile("");
    }
    uint32_t *words=(uint32_t *)(void *)holder;
    if(words[0x50/4]==0u){
        __asm volatile("cpsid i" ::: "memory");
        for(;;)__asm volatile("");
    }
    uint32_t held=--words[0x50/4];
    uint32_t base=words[0x4c/4];
    if(holder->priority!=base && held==0u){
        case_source_list_remove(&holder->state_item);
        holder->priority=base;
        holder->event_item.value=0x38u-base;
        if(CASE_STATE[4]<base)CASE_STATE[4]=base;
        case_source_list_insert_end((case_list *)(CASE_READY_BASE+base*20u),&holder->state_item);
        return 1;
    }
    return 0;
}
