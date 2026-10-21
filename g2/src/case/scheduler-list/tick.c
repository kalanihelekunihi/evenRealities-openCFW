#include "list_abi.h"

extern void case_reset_next_unblock(void);
#define CASE_STATE ((volatile uint32_t *)(uintptr_t)0x20000128u)
#define CASE_READY_BASE ((uintptr_t)0x20000ff4u)

/* Original xTaskIncrementTick at 0x0800ca78. The list/TCB addresses and
 * scheduler words are shared with waiter/resume source; callers provide
 * coherent active/overflow delayed lists and a current task when running. */
int32_t case_increment_tick(void)
{
    volatile uint32_t *state=CASE_STATE;
    if(state[12]!=0u){state[6]++;return 0;}
    uint32_t tick=state[3]+1u;
    state[3]=tick;
    if(tick==0u){
        case_list *active=(case_list *)(uintptr_t)state[13];
        if(active->count!=0u){__asm volatile("cpsid i" ::: "memory");for(;;)__asm volatile("");}
        uint32_t old=state[13];state[13]=state[14];state[14]=old;
        state[8]++;
        case_reset_next_unblock();
    }
    int32_t yielded=0;
    if(tick>=state[10]){
        case_list *active=(case_list *)(uintptr_t)state[13];
        while(active->count!=0u){
            case_tcb *task=(case_tcb *)active->end.next->owner;
            if(tick<task->state_item.value){state[10]=task->state_item.value;goto done_delayed;}
            case_source_list_remove(&task->state_item);
            if(task->event_item.container)case_source_list_remove(&task->event_item);
            uint32_t priority=task->priority;
            if(state[4]<priority)state[4]=priority;
            case_source_list_insert_end((case_list *)(CASE_READY_BASE+priority*20u),&task->state_item);
            if(((case_tcb *)(uintptr_t)state[0])->priority<=priority)yielded=1;
        }
        state[10]=0xffffffffu;
    }
done_delayed:
    if(((case_list *)(CASE_READY_BASE+((case_tcb *)(uintptr_t)state[0])->priority*20u))->count>1u)yielded=1;
    if(state[7]!=0u)yielded=1;
    return yielded;
}
