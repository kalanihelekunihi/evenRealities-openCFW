/* SPDX-License-Identifier: MIT
 * Native CASE 0xcb38 priority restoration after zero-width queue message.
 */
#include <stdint.h>
extern void case_policy_task_unlink(uint32_t link); /* 0xbf2c */
extern void case_policy_task_list_insert(uint32_t list,uint32_t link); /* 0xbfe2 */
static uint32_t rd(uint32_t a){return *(volatile uint32_t *)(uintptr_t)a;}
static void wr(uint32_t a,uint32_t v){*(volatile uint32_t *)(uintptr_t)a=v;}
static __attribute__((noreturn)) void native_fault(void)
{__asm__ volatile("cpsid i\n1: b 1b");__builtin_unreachable();}
uint32_t case_policy_task_notify_resume(uint32_t task)
{
    if(task==0u)return 0u;
    const uint32_t scheduler=0x20000128u;
    if(task!=rd(scheduler))native_fault();
    uint32_t depth=rd(task+80u);
    if(depth==0u)native_fault();
    --depth;
    wr(task+80u,depth);
    uint32_t inherited=rd(task+76u);
    if(rd(task+44u)==inherited || depth!=0u)return 0u;
    case_policy_task_unlink(task+4u);
    wr(task+44u,inherited);
    wr(task+24u,56u-inherited);
    if(inherited>rd(scheduler+16u))wr(scheduler+16u,inherited);
    case_policy_task_list_insert(0x20000ff4u+20u*inherited,task+4u);
    return 1u;
}
