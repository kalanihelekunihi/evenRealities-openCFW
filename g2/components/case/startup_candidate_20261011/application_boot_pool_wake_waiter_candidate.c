/* SPDX-License-Identifier: MIT
 * Native CASE 0x0800cba0: remove the first pool waiter and make it runnable.
 */
#include <stdint.h>
extern void case_policy_task_unlink(uint32_t link);
extern void case_policy_task_list_insert(uint32_t list, uint32_t link);
static uint32_t rd(uint32_t a){return *(volatile uint32_t *)(uintptr_t)a;}
static void wr(uint32_t a,uint32_t v){*(volatile uint32_t *)(uintptr_t)a=v;}
static __attribute__((noreturn)) void native_fault(void)
{__asm__ volatile("cpsid i\n1: b 1b");__builtin_unreachable();}
uint32_t case_boot_pool_wake_waiter(uint32_t list)
{
    uint32_t task=rd(rd(list+12u)+12u);
    if(task==0u)native_fault();
    case_policy_task_unlink(task+24u);
    const uint32_t scheduler=0x20000128u;
    if(rd(scheduler+48u)!=0u){
        case_policy_task_list_insert(0x2000147cu,task+24u);
    }else{
        case_policy_task_unlink(task+4u);
        uint32_t priority=rd(task+44u);
        if(priority>rd(scheduler+16u))wr(scheduler+16u,priority);
        case_policy_task_list_insert(0x20000ff4u+20u*priority,task+4u);
    }
    if(rd(task+44u)>rd(rd(scheduler)+44u)){
        wr(scheduler+28u,1u);
        return 1u;
    }
    return 0u;
}
