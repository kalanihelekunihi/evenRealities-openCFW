/* SPDX-License-Identifier: MIT
 * Native CASE 0x0800ca06 task creation wrapper and scheduler registration.
 */
#include <stdint.h>
extern void case_boot_task_initialize(void (*entry)(void *),const char *name,
                                      uint32_t stack_words,void *arg,uint32_t priority,
                                      uint32_t *created,uint32_t storage,uint32_t flags); /* 0xae96 */
extern void case_boot_task_register(uint32_t storage); /* 0xac08 */
static __attribute__((noreturn)) void native_fault(void)
{__asm__ volatile("cpsid i\n1: b 1b");__builtin_unreachable();}
uint32_t case_boot_task_create(void (*entry)(void *),const char *name,
                               uint32_t stack_words,void *arg,uint32_t priority,
                               uint32_t stack_end,uint32_t stack_start)
{
    if(stack_end==0u || stack_start==0u)native_fault();
    *(volatile uint32_t *)(uintptr_t)(stack_start+0x30u)=stack_end;
    *(volatile uint8_t *)(uintptr_t)(stack_start+0x59u)=2u;
    uint32_t created=0u;
    case_boot_task_initialize(entry,name,stack_words,arg,priority,&created,
                              stack_start,0u);
    case_boot_task_register(stack_start);
    return created;
}
