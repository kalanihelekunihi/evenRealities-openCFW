/* SPDX-License-Identifier: MIT
 * Stock 0x0800cc0c resume: flush pending-ready tasks, apply deferred ticks,
 * and request a context switch when the ready priority requires one.
 */
#include <stdint.h>
extern _Noreturn void case_kernel_invariant_failure(uint32_t condition);
extern void case_kernel_enter(void);
extern void case_kernel_exit(void);
extern uint32_t case_kernel_list_remove(uint32_t item);
extern void case_kernel_list_insert_tail(uint32_t list,uint32_t item);
extern uint32_t case_kernel_tick_increment(void); /* stock 0x0800ca78 */
extern void case_kernel_yield(void);
static volatile uint32_t *words(uint32_t address)
{return (volatile uint32_t *)(uintptr_t)address;}
#define SCHED 0x20000128u
#define READY 0x20000ff4u
#define PENDING 0x2000147cu

static void update_next_unblock(void)
{
    volatile uint32_t *state=words(SCHED);
    uint32_t list=state[0x34u/4u];
    if(words(list)[0]!=0u){
        uint32_t task=words(words(list)[3])[3];
        state[0x28u/4u]=words(task)[1];
    }else state[0x28u/4u]=0xffffffffu;
}

uint32_t case_kernel_scheduler_resume(void)
{
    volatile uint32_t *state=words(SCHED);
    if(state[0x30u/4u]==0u)case_kernel_invariant_failure(12u);
    uint32_t result=0u;
    case_kernel_enter();
    state[0x30u/4u]--;
    if(state[0x30u/4u]==0u && state[0x08u/4u]!=0u){
        uint32_t moved=0u;
        while(words(PENDING)[0]!=0u){
            uint32_t task=words(words(PENDING)[3])[3];
            case_kernel_list_remove(task+0x18u);
            case_kernel_list_remove(task+4u);
            uint32_t priority=words(task)[0x2cu/4u];
            if(state[0x10u/4u]<priority)state[0x10u/4u]=priority;
            case_kernel_list_insert_tail(READY+priority*0x14u,task+4u);
            if(words(state[0])[0x2cu/4u]<=priority)state[0x1cu/4u]=1u;
            moved=1u;
        }
        if(moved!=0u)update_next_unblock();
        uint32_t pending_ticks=state[0x18u/4u];
        if(pending_ticks!=0u){
            do{
                if(case_kernel_tick_increment()!=0u)state[0x1cu/4u]=1u;
                --pending_ticks;
            }while(pending_ticks!=0u);
            state[0x18u/4u]=0u;
        }
        if(state[0x1cu/4u]!=0u){result=1u;case_kernel_yield();}
    }
    case_kernel_exit();
    return result;
}
