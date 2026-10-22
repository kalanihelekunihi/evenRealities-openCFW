/* SPDX-License-Identifier: MIT
 * Native CASE 0x0800c390 ready-queue dispatch.
 */
#include <stdint.h>
static __attribute__((noreturn)) void native_fault(void)
{__asm__ volatile("cpsid i\n1: b 1b");__builtin_unreachable();}
static uint32_t rd(uint32_t a){return *(volatile uint32_t *)(uintptr_t)a;}
static void wr(uint32_t a,uint32_t v){*(volatile uint32_t *)(uintptr_t)a=v;}
/* Stock 0x0800C390 (vTaskSwitchContext) */
void case_policy_task_wake_dispatch(void)
{
    uint32_t scheduler=0x20000128u;
    if(rd(scheduler+48u)!=0u){wr(scheduler+28u,1u);return;}
    wr(scheduler+28u,0u);
    uint32_t priority=rd(scheduler+16u);
    while(rd(0x20000ff4u+priority*20u)==0u){
        if(priority==0u)native_fault();
        --priority;
    }
    uint32_t list=0x20000ff4u+priority*20u;
    uint32_t next=rd(rd(list+4u)+4u);
    wr(list+4u,next);
    if(next==list+8u)wr(list+4u,rd(next+4u));
    wr(scheduler,rd(rd(list+4u)+12u));
    wr(scheduler+16u,priority);
}
