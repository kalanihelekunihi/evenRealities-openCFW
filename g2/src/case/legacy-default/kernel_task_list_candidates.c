/* SPDX-License-Identifier: MIT
 * Queue wait/wake and mutex release from fixed CASE stock entries
 * 0x0800c178, 0x0800cba0 and 0x0800cb38. Task delay and scheduler tick
 * remain distinct typed contracts.
 */
#include <stdint.h>
extern _Noreturn void case_kernel_invariant_failure(uint32_t condition);
extern void case_kernel_list_insert_tail(uint32_t list,uint32_t item);
extern uint32_t case_kernel_list_remove(uint32_t item);
extern void case_kernel_list_insert_ordered(uint32_t list,uint32_t item);
extern void case_kernel_task_delay(uint32_t ticks,uint32_t allow_indefinite); /* 0x0800abb0 */
static volatile uint32_t *words(uint32_t address)
{return (volatile uint32_t *)(uintptr_t)address;}
#define SCHED 0x20000128u
#define READY 0x20000ff4u
#define PENDING 0x2000147cu

void case_queue_wait(uint32_t list,uint32_t ticks)
{
    if(list==0u)case_kernel_invariant_failure(9u);
    uint32_t task=words(SCHED)[0];
    case_kernel_list_insert_ordered(list,task+0x18u);
    case_kernel_task_delay(ticks,1u);
}

/* Stock 0x0800CBA0 (case_queue_wake) */
uint32_t case_queue_wake(uint32_t *list)
{
    uint32_t address=(uint32_t)(uintptr_t)list;
    uint32_t task=words(words(address)[3])[3];
    if(task==0u)case_kernel_invariant_failure(10u);
    case_kernel_list_remove(task+0x18u);
    volatile uint32_t *state=words(SCHED),*target=words(task);
    if(state[0x30u/4u]==0u){
        case_kernel_list_remove(task+4u);
        uint32_t priority=target[0x2cu/4u];
        if(state[0x10u/4u]<priority)state[0x10u/4u]=priority;
        case_kernel_list_insert_tail(READY+priority*0x14u,task+4u);
    }else case_kernel_list_insert_tail(PENDING,task+0x18u);
    if(words(state[0])[0x2cu/4u]<target[0x2cu/4u]){
        state[0x1cu/4u]=1u;
        return 1u;
    }
    return 0u;
}

/* Stock 0x0800CB38 (case_kernel_mutex_release) */
uint32_t case_kernel_mutex_release(uint32_t task)
{
    if(task==0u)return 0u;
    volatile uint32_t *state=words(SCHED),*target=words(task);
    if(task!=state[0] || target[0x50u/4u]==0u)
        case_kernel_invariant_failure(11u);
    uint32_t depth=target[0x50u/4u]-1u;
    target[0x50u/4u]=depth;
    if(target[0x2cu/4u]!=target[0x4cu/4u] && depth==0u){
        case_kernel_list_remove(task+4u);
        uint32_t priority=target[0x4cu/4u];
        target[0x2cu/4u]=priority;
        target[0x18u/4u]=0x38u-priority;
        if(state[0x10u/4u]<priority)state[0x10u/4u]=priority;
        case_kernel_list_insert_tail(READY+priority*0x14u,task+4u);
        return 1u;
    }
    return 0u;
}
