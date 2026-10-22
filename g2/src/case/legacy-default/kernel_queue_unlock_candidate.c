/* SPDX-License-Identifier: MIT
 * Stock 0x0800b374 deferred queue event release. The wake operation
 * retains its own typed task-list contract.
 */
#include <stdint.h>
extern void case_kernel_enter(void);
extern void case_kernel_exit(void);
extern uint32_t case_queue_wake(uint32_t *list);
extern void case_kernel_request_yield(void); /* stock 0x0800c16c */

/* Stock 0x0800B374 (case_queue_unlock) */
void case_queue_unlock(uint32_t queue)
{
    volatile int8_t *deferred_recv=(volatile int8_t *)(uintptr_t)(queue+0x45u);
    volatile int8_t *deferred_send=(volatile int8_t *)(uintptr_t)(queue+0x44u);
    case_kernel_enter();
    int8_t count=*deferred_recv;
    while(count>0){
        if(*(volatile uint32_t *)(uintptr_t)(queue+0x24u)==0u)break;
        if(case_queue_wake((uint32_t *)(uintptr_t)(queue+0x24u))!=0u)
            case_kernel_request_yield();
        --count;
    }
    *deferred_recv=-1;
    case_kernel_exit();
    case_kernel_enter();
    count=*deferred_send;
    while(count>0){
        if(*(volatile uint32_t *)(uintptr_t)(queue+0x10u)==0u)break;
        if(case_queue_wake((uint32_t *)(uintptr_t)(queue+0x10u))!=0u)
            case_kernel_request_yield();
        --count;
    }
    *deferred_send=-1;
    case_kernel_exit();
}

/* Stock 0x0800C16C (case_kernel_request_yield) */
void case_kernel_request_yield(void)
{
    *(volatile uint32_t *)(uintptr_t)0x20000144u=1u;
}
