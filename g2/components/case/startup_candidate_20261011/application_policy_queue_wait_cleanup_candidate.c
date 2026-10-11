/* SPDX-License-Identifier: MIT
 * Native CASE 0xb374 queue wake-drain cleanup and 0xc16c reschedule flag.
 */
#include <stdint.h>
extern void case_policy_scheduler_lock(void);
extern uint32_t case_policy_scheduler_unlock(void);
extern uint32_t case_boot_pool_wake_waiter(uint32_t list);
static uint32_t rd(uint32_t a){return *(volatile uint32_t *)(uintptr_t)a;}
static void wr(uint32_t a,uint32_t v){*(volatile uint32_t *)(uintptr_t)a=v;}
void case_policy_queue_wait_mark_reschedule(void)
{wr(0x20000128u+28u,1u);}
void case_policy_queue_wait_cleanup(uint32_t queue)
{
    case_policy_scheduler_lock();
    uint32_t payload=queue+64u;
    int8_t pending=*(volatile int8_t *)(uintptr_t)(payload+5u);
    while(pending>0 && rd(queue+36u)!=0u){
        if(case_boot_pool_wake_waiter(queue+36u)!=0u)case_policy_queue_wait_mark_reschedule();
        pending=(int8_t)(pending-1);
    }
    *(volatile uint8_t *)(uintptr_t)(payload+5u)=0xffu;
    (void)case_policy_scheduler_unlock();
    case_policy_scheduler_lock();
    pending=*(volatile int8_t *)(uintptr_t)(payload+4u);
    while(pending>0 && rd(queue+16u)!=0u){
        if(case_boot_pool_wake_waiter(queue+16u)!=0u)case_policy_queue_wait_mark_reschedule();
        pending=(int8_t)(pending-1);
    }
    *(volatile uint8_t *)(uintptr_t)(payload+4u)=0xffu;
    (void)case_policy_scheduler_unlock();
}
