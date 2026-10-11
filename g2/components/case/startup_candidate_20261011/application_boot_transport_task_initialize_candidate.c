/* SPDX-License-Identifier: MIT
 * Native CASE 0x0800af30 transport task record initialization.
 */
#include <stdint.h>
extern void case_boot_scheduler_initialize(void); /* 0xac84 */
extern void case_boot_task_link_reset(uint32_t link); /* 0xbfaa */
static __attribute__((noreturn)) void native_fault(void)
{__asm__ volatile("cpsid i\n1: b 1b" ::: "memory");__builtin_unreachable();}

void case_boot_transport_task_initialize(uint32_t entry,uint32_t priority,
    uint32_t mode,uint32_t context,uint32_t trampoline,uint32_t task)
{
    if(priority==0u)native_fault();
    if(task==0u)return;
    case_boot_scheduler_initialize();
    volatile uint32_t *record=(volatile uint32_t *)(uintptr_t)task;
    record[0u]=entry;
    record[6u]=priority;
    record[7u]=context;
    record[8u]=trampoline;
    case_boot_task_link_reset(task+4u);
    if(mode!=0u)*(volatile uint8_t *)(uintptr_t)(task+40u)|=4u;
}
