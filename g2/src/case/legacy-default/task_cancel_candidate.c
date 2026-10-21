/* SPDX-License-Identifier: MIT
 * Stock 0x0800ab26 cancellation guard and scheduler dispatch.
 * Scheduler lookup and queue operation remain typed kernel contracts.
 */
#include <stdint.h>
extern uint32_t case_task_lookup(uint32_t handle); /* stock 0x0800cde4 */
extern uint32_t case_task_signal(uint32_t handle,uint32_t event,
                                 uint32_t a,uint32_t b,uint32_t c); /* 0x0800cd80 */
uint32_t case_binary_56_cancel(uint32_t task)
{
    uint32_t control,exception=0u;
    __asm__ volatile("mrs %0, control" : "=r"(control));
    if((control&1u)==0u){
        __asm__ volatile("mrs %0, ipsr" : "=r"(exception));
        exception&=0x1fu;
    }
    if(exception!=0u) return UINT32_MAX-5u;
    if(task==0u) return UINT32_MAX-3u;
    if(case_task_lookup(task)==0u) return UINT32_MAX-2u;
    if(case_task_signal(task,3u,0u,0u,0u)!=1u) return UINT32_MAX;
    return 0u;
}
