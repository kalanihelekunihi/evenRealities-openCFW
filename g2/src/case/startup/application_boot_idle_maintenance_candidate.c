/* SPDX-License-Identifier: MIT
 * Native CASE 0x0800ace4 deferred task reclamation.
 */
#include <stdint.h>
extern void case_policy_scheduler_lock(void);
extern uint32_t case_policy_scheduler_unlock(void);
extern void case_policy_task_unlink(uint32_t link);
extern void case_boot_task_reclaim(uint32_t task); /* 0xadb8 */
static uint32_t rd(uint32_t a){return *(volatile uint32_t *)(uintptr_t)a;}
static void wr(uint32_t a,uint32_t v){*(volatile uint32_t *)(uintptr_t)a=v;}
/* Stock 0x0800ACE4 (case_boot_idle_maintenance) */
void case_boot_idle_maintenance(void)
{
    uint32_t scheduler=0x20000128u;
    uint32_t list=0x20001490u;
    while(rd(scheduler+4u)!=0u){
        case_policy_scheduler_lock();
        uint32_t task=rd(rd(list+12u)+12u);
        case_policy_task_unlink(task+4u);
        wr(scheduler+8u,rd(scheduler+8u)-1u);
        wr(scheduler+4u,rd(scheduler+4u)-1u);
        (void)case_policy_scheduler_unlock();
        case_boot_task_reclaim(task);
    }
}
