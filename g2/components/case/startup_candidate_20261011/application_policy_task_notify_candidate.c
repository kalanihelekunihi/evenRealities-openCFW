/* SPDX-License-Identifier: MIT
 * Native CASE task-notify wrapper 0x0800aa24.
 */
#include <stdint.h>
extern void case_policy_task_notify_core(uint32_t task); /* 0xc2f8 */
int32_t case_policy_task_notify(uint32_t task)
{
    uint32_t ipsr;
    __asm__ volatile("mrs %0, ipsr":"=r"(ipsr));
    if(ipsr!=0u)return -6;
    if(task==0u)return -4;
    case_policy_task_notify_core(task);
    return 0;
}
