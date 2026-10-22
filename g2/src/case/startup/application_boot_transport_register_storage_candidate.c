/* SPDX-License-Identifier: MIT
 * Native CASE 0x0800ccc0/0x0800ccf2 dynamic/static task storage selection.
 */
#include <stdint.h>
extern uint32_t case_boot_transport_heap_allocate(uint32_t bytes); /* 0xb3e8 */
extern void case_boot_transport_task_initialize(uint32_t entry,uint32_t priority,
    uint32_t mode,uint32_t context,uint32_t trampoline,uint32_t task); /* 0xaf30 */
static __attribute__((noreturn)) void native_fault(void)
{__asm__ volatile("cpsid i\n1: b 1b" ::: "memory");__builtin_unreachable();}

/* Stock 0x0800CCC0 (case_boot_transport_register_dynamic) */
uint32_t case_boot_transport_register_dynamic(uint32_t entry,uint32_t priority,
    uint32_t mode,uint32_t context,uint32_t trampoline)
{
    uint32_t task=case_boot_transport_heap_allocate(44u);
    if(task!=0u){
        *(volatile uint8_t *)(uintptr_t)(task+40u)=0u;
        case_boot_transport_task_initialize(entry,priority,mode,context,trampoline,task);
    }
    return task;
}

/* Stock 0x0800CCF2 (case_boot_transport_register_static) */
uint32_t case_boot_transport_register_static(uint32_t entry,uint32_t priority,
    uint32_t mode,uint32_t context,uint32_t trampoline,uint32_t task)
{
    if(task==0u)native_fault();
    *(volatile uint8_t *)(uintptr_t)(task+40u)=2u;
    case_boot_transport_task_initialize(entry,priority,mode,context,trampoline,task);
    return task;
}
