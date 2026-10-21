/* SPDX-License-Identifier: MIT
 * Native CASE 0x0800ac84 scheduler list and pool initialization.
 */
#include <stdint.h>
extern void case_policy_scheduler_lock(void);
extern uint32_t case_policy_scheduler_unlock(void);
extern void case_policy_task_list_initialize(uint32_t list); /* 0xbf94 */
extern uint32_t case_boot_scheduler_pool(uint32_t count,uint32_t stride,uint32_t storage,
                                         uint32_t region,uint32_t flags); /* 0xc5d0 */
extern void case_boot_scheduler_register(uint32_t scheduler,const char *name); /* 0xc0b8 */
extern const char case_boot_scheduler_name[]; /* linker data 0xacdc */
void case_boot_scheduler_initialize(void)
{
    case_policy_scheduler_lock();
    volatile uint32_t *state=(volatile uint32_t *)(uintptr_t)0x20000164u;
    if(state[0]==0u){
        case_policy_task_list_initialize(0x200015a8u);
        case_policy_task_list_initialize(0x200015bcu);
        state[3]=0x200015a8u;
        state[4]=0x200015bcu;
        uint32_t scheduler=case_boot_scheduler_pool(10u,16u,0x20001508u,
                                                    0x200014b8u,0u);
        state[0]=scheduler;
        if(scheduler!=0u)case_boot_scheduler_register(scheduler,case_boot_scheduler_name);
    }
    (void)case_policy_scheduler_unlock();
}
