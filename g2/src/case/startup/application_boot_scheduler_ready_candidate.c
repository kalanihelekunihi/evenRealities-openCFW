/* SPDX-License-Identifier: MIT
 * Native CASE 0x0800cd20 scheduler initialization and service task creation.
 */
#include <stdint.h>
extern void case_boot_scheduler_initialize(void); /* 0xac84 */
extern void case_boot_service_task_entry(void *arg); /* 0xb360 */
extern const char case_boot_service_task_name[]; /* linker data at 0xcd74 */
extern uint32_t case_boot_task_create(void (*entry)(void *),const char *name,
                                      uint32_t stack_words,void *arg,uint32_t priority,
                                      uint32_t stack_end,uint32_t stack_start); /* 0xca06 */
static __attribute__((noreturn)) void native_fault(void)
{__asm__ volatile("cpsid i\n1: b 1b");__builtin_unreachable();}
uint32_t case_boot_scheduler_ready(void)
{
    case_boot_scheduler_initialize();
    volatile uint32_t *state=(volatile uint32_t *)(uintptr_t)0x20000164u;
    if(state[0]==0u)native_fault();
    uint32_t task=case_boot_task_create(case_boot_service_task_entry,
                                        case_boot_service_task_name,0x100u,0,2u,
                                        0x20001888u,0x2000182cu);
    state[1]=task;
    if(task==0u)native_fault();
    return 1u;
}
