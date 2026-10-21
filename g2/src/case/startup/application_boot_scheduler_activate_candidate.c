/* SPDX-License-Identifier: MIT
 * Native CASE 0x0800c284 idle-task creation and scheduler activation.
 */
#include <stdint.h>
extern void case_boot_idle_task_entry(void *arg); /* native 0xae5c */
extern const char case_boot_idle_task_name[5]; /* product/linker data 0xc2e8 */
extern uint32_t case_boot_task_create(void (*entry)(void *),const char *name,
                                      uint32_t stack_words,void *arg,uint32_t priority,
                                      uint32_t stack_end,uint32_t stack_start); /* 0xca06 */
extern uint32_t case_boot_scheduler_ready(void); /* 0xcd20 */
extern void case_boot_scheduler_run(void); /* 0xc57c */
static __attribute__((noreturn)) void native_fault(void)
{__asm__ volatile("cpsid i\n1: b 1b");__builtin_unreachable();}
void case_boot_scheduler_activate(void)
{
    uint32_t task=case_boot_task_create(case_boot_idle_task_entry,
                                        case_boot_idle_task_name,0x80u,0,0u,
                                        0x2000162cu,0x200015d0u);
    volatile uint32_t *scheduler=(volatile uint32_t *)(uintptr_t)0x20000128u;
    scheduler[11]=task;
    uint32_t status=task!=0u?case_boot_scheduler_ready():0u;
    if(status==1u){
        __asm__ volatile("cpsid i" ::: "memory");
        scheduler[10]=0xffffffffu;
        scheduler[5]=1u;
        scheduler[3]=0u;
        case_boot_scheduler_run();
        return;
    }
    if(status==0xffffffffu)native_fault();
}
