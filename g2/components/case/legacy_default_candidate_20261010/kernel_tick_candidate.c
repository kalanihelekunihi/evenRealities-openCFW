/* SPDX-License-Identifier: MIT
 * Stock 0x0800ca78 scheduler tick update. Delayed-list entry and task
 * priority layout are from the retained fixed-image scheduler ABI.
 */
#include <stdint.h>
extern _Noreturn void case_kernel_invariant_failure(uint32_t condition);
extern uint32_t case_kernel_list_remove(uint32_t item);
extern void case_kernel_list_insert_tail(uint32_t list,uint32_t item);
static volatile uint32_t *words(uint32_t address)
{return (volatile uint32_t *)(uintptr_t)address;}
#define SCHED 0x20000128u
#define READY 0x20000ff4u

static void update_next_unblock(void)
{
    volatile uint32_t *state=words(SCHED);
    uint32_t list=state[0x34u/4u];
    if(words(list)[0]!=0u){
        uint32_t task=words(words(list)[3])[3];
        state[0x28u/4u]=words(task)[1];
    }else state[0x28u/4u]=0xffffffffu;
}

uint32_t case_kernel_tick_increment(void)
{
    volatile uint32_t *state=words(SCHED);
    uint32_t switch_needed=0u;
    if(state[0x30u/4u]!=0u){state[0x18u/4u]++;return 0u;}
    uint32_t now=state[0x0cu/4u]+1u;
    state[0x0cu/4u]=now;
    if(now==0u){
        if(words(state[0x34u/4u])[0]!=0u)case_kernel_invariant_failure(13u);
        uint32_t current=state[0x34u/4u];
        state[0x34u/4u]=state[0x38u/4u];
        state[0x38u/4u]=current;
        state[0x20u/4u]++;
        update_next_unblock();
    }
    if(state[0x28u/4u]<=now){
        while(words(state[0x34u/4u])[0]!=0u){
            uint32_t task=words(words(state[0x34u/4u])[3])[3];
            if(now<words(task+4u)[0]){
                state[0x28u/4u]=words(task+4u)[0];
                break;
            }
            case_kernel_list_remove(task+4u);
            if(words(task)[0x28u/4u]!=0u)case_kernel_list_remove(task+0x18u);
            uint32_t priority=words(task)[0x2cu/4u];
            if(state[0x10u/4u]<priority)state[0x10u/4u]=priority;
            case_kernel_list_insert_tail(READY+priority*0x14u,task+4u);
            if(words(state[0])[0x2cu/4u]<=priority)switch_needed=1u;
        }
        if(words(state[0x34u/4u])[0]==0u)state[0x28u/4u]=0xffffffffu;
    }
    if(words(READY+words(state[0])[0x2cu/4u]*0x14u)[0]>1u)switch_needed=1u;
    if(state[0x1cu/4u]!=0u)switch_needed=1u;
    return switch_needed;
}
