/* SPDX-License-Identifier: MIT
 * Native CASE 0xc686 task-context queue send, including the wait/retry loop.
 */
#include <stdint.h>
extern uint32_t case_policy_scheduler_mode(void); /* 0xca4c */
extern void case_policy_scheduler_lock(void); /* 0xbffc */
extern uint32_t case_policy_scheduler_unlock(void); /* 0xc014 */
extern uint32_t case_policy_task_reschedule(void); /* 0xc0a0 */
extern uint32_t case_policy_message_copy(uint32_t queue,const uint32_t *args,uint32_t mode); /* 0xad48 */
extern uint32_t case_boot_pool_wake_waiter(uint32_t list); /* 0xcba0 */
extern void case_policy_queue_wait_snapshot(uint32_t *snapshot); /* 0xc15c */
extern void case_policy_task_sleep_enter(void); /* 0xc380 */
extern uint32_t case_policy_queue_wait_elapsed(uint32_t *snapshot,uint32_t *timeout); /* 0xc948 */
extern void case_policy_queue_wait_cleanup(uint32_t queue); /* 0xb374 */
extern uint32_t case_policy_task_sleep_exit(void); /* 0xcc0c */
extern uint32_t case_policy_queue_wait_eligible(uint32_t queue); /* 0xb080 */
extern void case_policy_queue_wait_register(uint32_t list,uint32_t timeout); /* 0xc178 */
static uint32_t rd(uint32_t a){return *(volatile uint32_t *)(uintptr_t)a;}
static void wr8(uint32_t a,uint8_t v){*(volatile uint8_t *)(uintptr_t)a=v;}
static __attribute__((noreturn)) void native_fault(void)
{__asm__ volatile("cpsid i\n1: b 1b");__builtin_unreachable();}
/* Stock 0x0800C686 (case_policy_task_message_send) */
uint32_t case_policy_task_message_send(uint32_t queue,const uint32_t *args,uint32_t timeout,uint32_t mode,uint32_t metadata)
{
    (void)metadata;
    if(queue==0u)native_fault();
    if(args==0 && rd(queue+64u)!=0u)native_fault();
    if(mode==2u && rd(queue+60u)!=1u)native_fault();
    if(case_policy_scheduler_mode()==0u && timeout!=0u)native_fault();
    uint32_t snapshot[2]={0u,0u};
    uint32_t waited=0u;
    uint32_t waiter_list=queue+16u;
    uint32_t receive_list=queue+36u;
    uint32_t payload=queue+64u;
    for(;;){
        case_policy_scheduler_lock();
        uint32_t count=rd(queue+56u),capacity=rd(queue+60u);
        if(count<capacity || mode==2u){
            uint32_t copied=case_policy_message_copy(queue,args,mode);
            if(rd(receive_list)!=0u){
                if(case_boot_pool_wake_waiter(receive_list)!=0u)case_policy_task_reschedule();
            }else if(copied!=0u)case_policy_task_reschedule();
            (void)case_policy_scheduler_unlock();
            return 1u;
        }
        if(timeout==0u){(void)case_policy_scheduler_unlock();return 0u;}
        if(waited==0u){case_policy_queue_wait_snapshot(snapshot);waited=1u;}
        (void)case_policy_scheduler_unlock();
        case_policy_task_sleep_enter();
        case_policy_scheduler_lock();
        if((int8_t)*(volatile uint8_t *)(uintptr_t)(payload+4u)==-1)wr8(payload+4u,0u);
        if((int8_t)*(volatile uint8_t *)(uintptr_t)(payload+5u)==-1)wr8(payload+5u,0u);
        (void)case_policy_scheduler_unlock();
        if(case_policy_queue_wait_elapsed(snapshot,&timeout)!=0u){
            case_policy_queue_wait_cleanup(queue);
            (void)case_policy_task_sleep_exit();
            return 0u;
        }
        if(case_policy_queue_wait_eligible(queue)!=0u){
            case_policy_queue_wait_register(waiter_list,timeout);
            case_policy_queue_wait_cleanup(queue);
            if(case_policy_task_sleep_exit()==0u)case_policy_task_reschedule();
        }else{
            case_policy_queue_wait_cleanup(queue);
            (void)case_policy_task_sleep_exit();
        }
    }
}
