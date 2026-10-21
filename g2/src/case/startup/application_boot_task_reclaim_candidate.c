/* SPDX-License-Identifier: MIT
 * Native CASE 0x0800adb8 ownership-based task reclamation.
 */
#include <stdint.h>
extern void case_boot_heap_free(uint32_t address); /* 0xc030 */
static __attribute__((noreturn)) void native_fault(void)
{__asm__ volatile("cpsid i\n1: b 1b");__builtin_unreachable();}
void case_boot_task_reclaim(uint32_t task)
{
    uint8_t owner=*(volatile uint8_t *)(uintptr_t)(task+0x59u);
    if(owner==0u){
        uint32_t stack=*(volatile uint32_t *)(uintptr_t)(task+0x30u);
        case_boot_heap_free(stack);
        case_boot_heap_free(task);
    }else if(owner==1u)case_boot_heap_free(task);
    else if(owner!=2u)native_fault();
}
