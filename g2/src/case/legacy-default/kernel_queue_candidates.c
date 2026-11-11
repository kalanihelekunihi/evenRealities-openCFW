/* SPDX-License-Identifier: MIT
 * Stock 0x0800c7a8 queue post and 0x0800c686 blocking queue send.
 * Queue storage, wakeups, scheduler suspension and timebase are typed
 * platform contracts. Invalid-state halt is delegated to the platform.
 */
#include <stdint.h>
extern _Noreturn void case_kernel_invariant_failure(uint32_t condition);
extern uint32_t case_kernel_irq_save(void);                   /* 0x080000f4 */
extern void case_kernel_irq_restore(uint32_t token);         /* 0x080000fc */
extern uint32_t case_queue_copy_in(uint32_t queue,const void *item,uint32_t mode); /* 0x0800ad48 */
extern uint32_t case_queue_wake(uint32_t *list);             /* 0x0800cba0 */
extern void case_kernel_yield(void);                          /* 0x0800c0a0 */
extern void case_kernel_enter(void);
extern void case_kernel_exit(void);
extern uint32_t case_kernel_mode(void);
extern void case_kernel_timeout_start(uint32_t state[2]);   /* 0x0800c15c */
extern void case_kernel_scheduler_suspend(void);             /* 0x0800c380 */
extern uint32_t case_kernel_timeout_check(uint32_t state[2],uint32_t *ticks); /* 0x0800c948 */
extern uint32_t case_queue_is_active(uint32_t queue);        /* 0x0800b080 */
extern void case_queue_unlock(uint32_t queue);               /* 0x0800b374 */
extern void case_queue_wait(uint32_t list,uint32_t ticks);   /* 0x0800c178 */
extern uint32_t case_kernel_scheduler_resume(void);          /* 0x0800cc0c */
static uint32_t word(uint32_t base,uint32_t offset)
{return *(volatile uint32_t *)(uintptr_t)(base+offset);}
uint32_t case_kernel_queue_post(uint32_t queue,const void *item,
                                uint32_t *woken,uint32_t mode)
{
    if(queue==0u)case_kernel_invariant_failure(1u);
    if(item==0 && word(queue,0x40u)!=0u)case_kernel_invariant_failure(2u);
    if(mode==2u && word(queue,0x3cu)!=1u)case_kernel_invariant_failure(3u);
    uint32_t token=case_kernel_irq_save();
    uint32_t result=0u;
    if(word(queue,0x38u)<word(queue,0x3cu)||mode==2u){
        int8_t waiting=*(volatile int8_t *)(uintptr_t)(queue+0x45u);
        (void)case_queue_copy_in(queue,item,mode);
        if(waiting==-1){
            if(word(queue,0x24u)!=0u && case_queue_wake((uint32_t *)(uintptr_t)(queue+0x24u))!=0u && woken!=0)
                *woken=1u;
        }else *(volatile int8_t *)(uintptr_t)(queue+0x45u)=(int8_t)(waiting+1);
        result=1u;
    }
    case_kernel_irq_restore(token);
    return result;
}
/* Dedup (0x0800c686): case_kernel_queue_send is an alias of case_policy_task_message_send (startup/application_policy_task_message_send_candidate.c). */
extern uint32_t case_kernel_queue_send(uint32_t queue,const void *item, uint32_t timeout,uint32_t mode);
/* Dedup (0x0800c7a8): case_policy_task_message_special (was startup/application_policy_task_message_special_candidate.c). */
uint32_t case_policy_task_message_special(uint32_t scheduler,const uint32_t *args,uint32_t notify,uint32_t mode,uint32_t meta) __attribute__((alias("case_kernel_queue_post")));
