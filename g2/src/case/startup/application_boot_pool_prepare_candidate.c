/* SPDX-License-Identifier: MIT
 * Native CASE 0x0800c616 pool free-list setup and waiter wake.
 */
#include <stdint.h>
extern void case_policy_scheduler_lock(void);
extern uint32_t case_policy_scheduler_unlock(void);
extern void case_policy_task_list_initialize(uint32_t list);
extern uint32_t case_boot_pool_wake_waiter(uint32_t list); /* 0xcba0 */
extern uint32_t case_policy_task_reschedule(void);
static __attribute__((noreturn)) void native_fault(void)
{__asm__ volatile("cpsid i\n1: b 1b");__builtin_unreachable();}
static uint32_t rd(uint32_t a){return *(volatile uint32_t *)(uintptr_t)a;}
static void wr(uint32_t a,uint32_t v){*(volatile uint32_t *)(uintptr_t)a=v;}
/* Stock 0x0800C616 (case_boot_pool_prepare) */
uint32_t case_boot_pool_prepare(uint32_t region,uint32_t mode)
{
    if(region==0u)native_fault();
    case_policy_scheduler_lock();
    uint32_t count=rd(region+0x3cu),stride=rd(region+0x40u),storage=rd(region);
    wr(region+8u,storage+count*stride);
    wr(region+0x38u,0u);
    wr(region+4u,storage);
    wr(region+12u,storage+(count-1u)*stride);
    *(volatile uint8_t *)(uintptr_t)(region+0x44u)=0xffu;
    *(volatile uint8_t *)(uintptr_t)(region+0x45u)=0xffu;
    if(mode!=0u){
        case_policy_task_list_initialize(region+16u);
        case_policy_task_list_initialize(region+36u);
    }else if(rd(region+16u)!=0u && case_boot_pool_wake_waiter(region+16u)!=0u)
        (void)case_policy_task_reschedule();
    (void)case_policy_scheduler_unlock();
    return 1u;
}
