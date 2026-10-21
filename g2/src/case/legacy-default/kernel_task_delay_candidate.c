/* SPDX-License-Identifier: MIT
 * Stock 0x0800abb0 task delay: move current task from ready list to the
 * indefinite or time-ordered wait list.
 */
#include <stdint.h>
extern uint32_t case_kernel_list_remove(uint32_t item);
extern void case_kernel_list_insert_tail(uint32_t list,uint32_t item);
extern void case_kernel_list_insert_ordered(uint32_t list,uint32_t item);
static volatile uint32_t *words(uint32_t address)
{return (volatile uint32_t *)(uintptr_t)address;}

void case_kernel_task_delay(uint32_t ticks,uint32_t allow_indefinite)
{
    volatile uint32_t *state=words(0x20000128u);
    uint32_t now=state[0x0cu/4u];
    uint32_t task=state[0];
    case_kernel_list_remove(task+4u);
    if(ticks==0xffffffffu && allow_indefinite!=0u){
        case_kernel_list_insert_tail(0x200014a4u,task+4u);
        return;
    }
    uint32_t wake=now+ticks;
    words(task+4u)[0]=wake;
    if(wake<now)case_kernel_list_insert_ordered(state[0x38u/4u],task+4u);
    else{
        case_kernel_list_insert_ordered(state[0x34u/4u],task+4u);
        if(wake<state[0x28u/4u])state[0x28u/4u]=wake;
    }
}
