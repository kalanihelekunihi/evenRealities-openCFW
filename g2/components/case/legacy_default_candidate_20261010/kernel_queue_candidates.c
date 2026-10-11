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
uint32_t case_kernel_queue_send(uint32_t queue,const void *item,
                                uint32_t timeout,uint32_t mode)
{
    if(queue==0u)case_kernel_invariant_failure(4u);
    if(item==0 && word(queue,0x40u)!=0u)case_kernel_invariant_failure(5u);
    if(mode==2u && word(queue,0x3cu)!=1u)case_kernel_invariant_failure(6u);
    if(case_kernel_mode()==0u && timeout!=0u)case_kernel_invariant_failure(7u);
    uint32_t clock[2]={0u,0u};
    uint32_t started=0u;
    for(;;){
        case_kernel_enter();
        if(word(queue,0x38u)<word(queue,0x3cu)||mode==2u){
            uint32_t copied=case_queue_copy_in(queue,item,mode);
            if(word(queue,0x24u)==0u){
                if(copied!=0u)case_kernel_yield();
            }else if(case_queue_wake((uint32_t *)(uintptr_t)(queue+0x24u))!=0u)
                case_kernel_yield();
            case_kernel_exit();
            return 1u;
        }
        if(timeout==0u){case_kernel_exit();return 0u;}
        if(started==0u){case_kernel_timeout_start(clock);started=1u;}
        case_kernel_exit();
        case_kernel_scheduler_suspend();
        case_kernel_enter();
        volatile int8_t *sendwait=(volatile int8_t *)(uintptr_t)(queue+0x44u);
        volatile int8_t *recvwait=(volatile int8_t *)(uintptr_t)(queue+0x45u);
        if(*sendwait==-1)*sendwait=0;
        if(*recvwait==-1)*recvwait=0;
        case_kernel_exit();
        if(case_kernel_timeout_check(clock,&timeout)!=0u)break;
        if(case_queue_is_active(queue)==0u){
            case_queue_unlock(queue);
            (void)case_kernel_scheduler_resume();
        }else{
            case_queue_wait(queue+0x10u,timeout);
            case_queue_unlock(queue);
            if(case_kernel_scheduler_resume()==0u)case_kernel_yield();
        }
    }
    case_queue_unlock(queue);
    (void)case_kernel_scheduler_resume();
    return 0u;
}
