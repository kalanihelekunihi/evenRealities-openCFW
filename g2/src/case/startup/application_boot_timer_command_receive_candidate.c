/* SPDX-License-Identifier: MIT
 * CASE native 0xc83a task queue receive, its 0xad24 copy-out and 0xb064
 * zero-count predicate. The branch order is shared with native 0xc686 send.
 */
#include <stdint.h>
extern uint32_t case_policy_scheduler_mode(void); /* 0xca4c */
extern void case_policy_scheduler_lock(void); /* 0xbffc */
extern uint32_t case_policy_scheduler_unlock(void); /* 0xc014 */
extern uint32_t case_policy_task_reschedule(void); /* 0xc0a0 */
extern uint32_t case_boot_pool_wake_waiter(uint32_t list); /* 0xcba0 */
extern void case_policy_queue_wait_snapshot(uint32_t *snapshot); /* 0xc15c */
extern void case_policy_task_sleep_enter(void); /* 0xc380 */
extern uint32_t case_policy_queue_wait_elapsed(uint32_t *snapshot,uint32_t *timeout); /* 0xc948 */
extern void case_policy_queue_wait_cleanup(uint32_t queue); /* 0xb374 */
extern uint32_t case_policy_task_sleep_exit(void); /* 0xcc0c */
extern void case_policy_queue_wait_register(uint32_t list,uint32_t timeout); /* 0xc178 */
static uint32_t rd(uint32_t a){return *(volatile uint32_t *)(uintptr_t)a;}
static void wr(uint32_t a,uint32_t v){*(volatile uint32_t *)(uintptr_t)a=v;}
static uint8_t rb(uint32_t a){return *(volatile uint8_t *)(uintptr_t)a;}
static void wb(uint32_t a,uint8_t v){*(volatile uint8_t *)(uintptr_t)a=v;}
static __attribute__((noreturn)) void native_fault(void)
{__asm__ volatile("cpsid i\n1: b 1b");__builtin_unreachable();}
static void copy_bytes(uint32_t destination,uint32_t source,uint32_t count)
{for(uint32_t i=0u;i<count;++i)*(volatile uint8_t *)(uintptr_t)(destination+i)=rb(source+i);}
static void copy_out(uint32_t queue,uint32_t destination)
{
    uint32_t size=rd(queue+64u);
    if(size==0u)return;
    uint32_t read=rd(queue+12u)+size;
    wr(queue+12u,read);
    if(read>=rd(queue+8u)){read=rd(queue);wr(queue+12u,read);}
    copy_bytes(destination,read,size);
}
static uint32_t is_empty(uint32_t queue)
{
    case_policy_scheduler_lock();
    uint32_t result=rd(queue+56u)==0u;
    (void)case_policy_scheduler_unlock();
    return result;
}
uint32_t case_boot_timer_command_receive(uint32_t queue,uint32_t *message,uint32_t timeout)
{
    if(queue==0u)native_fault();
    if(message==0 && rd(queue+64u)!=0u)native_fault();
    if(case_policy_scheduler_mode()==0u && timeout!=0u)native_fault();
    uint32_t snapshot[2]={0u,0u};
    uint32_t waited=0u;
    for(;;){
        case_policy_scheduler_lock();
        uint32_t count=rd(queue+56u);
        if(count!=0u){
            copy_out(queue,(uint32_t)(uintptr_t)message);
            wr(queue+56u,count-1u);
            if(rd(queue+16u)!=0u && case_boot_pool_wake_waiter(queue+16u)!=0u)
                (void)case_policy_task_reschedule();
            (void)case_policy_scheduler_unlock();
            return 1u;
        }
        if(timeout==0u){(void)case_policy_scheduler_unlock();return 0u;}
        if(waited==0u){case_policy_queue_wait_snapshot(snapshot);waited=1u;}
        (void)case_policy_scheduler_unlock();
        case_policy_task_sleep_enter();
        case_policy_scheduler_lock();
        if((int8_t)rb(queue+68u)==-1)wb(queue+68u,0u);
        if((int8_t)rb(queue+69u)==-1)wb(queue+69u,0u);
        (void)case_policy_scheduler_unlock();
        if(case_policy_queue_wait_elapsed(snapshot,&timeout)!=0u){
            case_policy_queue_wait_cleanup(queue);
            (void)case_policy_task_sleep_exit();
            if(is_empty(queue)!=0u)return 0u;
        }else if(is_empty(queue)!=0u){
            case_policy_queue_wait_register(queue+36u,timeout);
            case_policy_queue_wait_cleanup(queue);
            if(case_policy_task_sleep_exit()==0u)(void)case_policy_task_reschedule();
        }else{
            case_policy_queue_wait_cleanup(queue);
            (void)case_policy_task_sleep_exit();
        }
    }
}
