#include "list_abi.h"

extern void case_enter_critical(void);
extern void case_exit_critical(void);
extern uint32_t case_yield_request(void);
/* Original 0x0800ca78 is a distinct lower provider. */
extern int32_t case_increment_tick(void);

#define CASE_STATE ((volatile uint32_t *)(uintptr_t)0x20000128u)
#define CASE_PENDING ((case_list *)(uintptr_t)0x2000147cu)
#define CASE_READY_BASE ((uintptr_t)0x20000ff4u)

/* Original 0x0800b260. The active delayed list pointer lives at state+0x34. */
/* Stock 0x0800B260 (case_reset_next_unblock) */
void case_reset_next_unblock(void)
{
    case_list *delayed=(case_list *)(uintptr_t)CASE_STATE[13];
    CASE_STATE[10]=delayed->count ? ((case_tcb *)delayed->end.next->owner)->state_item.value : 0xffffffffu;
}

/* Original 0x0800cc0c; xTaskIncrementTick remains an explicit lower
 * provider with original ABI and shared scheduler/list state. */
int32_t case_resume_scheduler(void)
{
    volatile uint32_t *state=CASE_STATE;
    if(state[12]==0u){__asm volatile("cpsid i" ::: "memory");for(;;)__asm volatile("");}
    case_enter_critical();
    state[12]--;
    int32_t yielded=0;
    if(state[12]==0u && state[2]!=0u){
        case_tcb *last=0;
        while(CASE_PENDING->count!=0u){
            case_tcb *task=(case_tcb *)CASE_PENDING->end.next->owner;
            case_source_list_remove(&task->event_item);
            case_source_list_remove(&task->state_item);
            uint32_t priority=task->priority;
            if(state[4]<priority)state[4]=priority;
            case_source_list_insert_end((case_list *)(CASE_READY_BASE+priority*20u),&task->state_item);
            if(((case_tcb *)(uintptr_t)state[0])->priority<=priority)state[7]=1u;
            last=task;
        }
        if(last)case_reset_next_unblock();
        uint32_t ticks=state[6];
        while(ticks!=0u){
            if(case_increment_tick()!=0)state[7]=1u;
            --ticks;
        }
        if(state[6]!=0u)state[6]=0u;
        if(state[7]!=0u){yielded=1; (void)case_yield_request();}
    }
    case_exit_critical();
    return yielded;
}
