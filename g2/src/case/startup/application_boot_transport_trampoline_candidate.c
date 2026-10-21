/* SPDX-License-Identifier: MIT
 * Native CASE 0x08008558 callback trampoline and 0x0800b4a4 context lookup.
 */
#include <stdint.h>
extern void case_policy_scheduler_lock(void); /* 0xbffc */
extern uint32_t case_policy_scheduler_unlock(void); /* 0xc014 */
static __attribute__((noreturn)) void native_fault(void)
{__asm__ volatile("cpsid i\n1: b 1b" ::: "memory");__builtin_unreachable();}

uint32_t case_boot_transport_task_context(uint32_t task)
{
    if(task==0u)native_fault();
    case_policy_scheduler_lock();
    uint32_t context=*(volatile uint32_t *)(uintptr_t)(task+28u);
    (void)case_policy_scheduler_unlock();
    return context;
}

void case_boot_transport_entry_8558(uint32_t task)
{
    uint32_t context=case_boot_transport_task_context(task);
    if(context!=0u){
        volatile const uint32_t *pair=(volatile const uint32_t *)(uintptr_t)context;
        void (*callback)(uint32_t)=(void (*)(uint32_t))(uintptr_t)pair[0u];
        callback(pair[1u]);
    }
}
