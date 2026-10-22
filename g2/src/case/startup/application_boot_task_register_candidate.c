/* SPDX-License-Identifier: MIT
 * Native CASE 0x0800ac08 task ready-queue registration.
 */
#include <stdint.h>
extern void case_policy_scheduler_lock(void);
extern uint32_t case_policy_scheduler_unlock(void);
extern void case_policy_task_list_insert(uint32_t list,uint32_t link);
extern uint32_t case_policy_task_reschedule(void);
extern void case_boot_first_task_prepare(void); /* 0xaf70 */
static uint32_t rd(uint32_t a){return *(volatile uint32_t *)(uintptr_t)a;}
static void wr(uint32_t a,uint32_t v){*(volatile uint32_t *)(uintptr_t)a=v;}
/* Stock 0x0800AC08 (case_boot_task_register) */
void case_boot_task_register(uint32_t task)
{
    uint32_t scheduler=0x20000128u;
    case_policy_scheduler_lock();
    uint32_t count=rd(scheduler+8u)+1u;wr(scheduler+8u,count);
    uint32_t current=rd(scheduler);
    if(current==0u){
        wr(scheduler,task);
        if(count==1u)case_boot_first_task_prepare();
    }else if(rd(scheduler+20u)==0u && rd(current+44u)<=rd(task+44u))
        wr(scheduler,task);
    uint32_t sequence=rd(scheduler+36u)+1u;
    wr(scheduler+36u,sequence);wr(task+68u,sequence);
    uint32_t priority=rd(task+44u);
    if(priority>rd(scheduler+16u))wr(scheduler+16u,priority);
    case_policy_task_list_insert(0x20000ff4u+priority*20u,task+4u);
    (void)case_policy_scheduler_unlock();
    if(rd(scheduler+20u)!=0u && rd(rd(scheduler)+44u)<priority)
        (void)case_policy_task_reschedule();
}
