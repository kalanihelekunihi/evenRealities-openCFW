/* SPDX-License-Identifier: MIT
 * Native CASE 0x0800c9a8 dynamic worker allocation and 0x0800ca06 static
 * worker creation, sharing the already sourced task initializer.
 */
#include <stdint.h>
extern uint32_t case_boot_transport_heap_allocate(uint32_t bytes); /* 0xb3e8 */
extern void case_boot_heap_free(uint32_t address); /* 0xc030 */
extern void case_boot_task_initialize(void (*entry)(void *),const char *name,
    uint32_t stack_words,void *arg,uint32_t priority,uint32_t *created,
    uint32_t storage,uint32_t flags); /* 0xae96 */
extern void case_boot_task_register(uint32_t storage); /* 0xac08 */
extern uint32_t case_boot_task_create(void (*entry)(void *),const char *name,
    uint32_t stack_words,void *arg,uint32_t priority,
    uint32_t stack_end,uint32_t stack_start); /* 0xca06 */

uint32_t case_boot_transport_worker_dynamic(uint32_t entry,uint32_t name,
    uint32_t stack_words,uint32_t arg,uint32_t priority,uint32_t *task)
{
    uint32_t stack=case_boot_transport_heap_allocate(stack_words*4u);
    uint32_t record=0u;
    if(stack!=0u){
        record=case_boot_transport_heap_allocate(92u);
        if(record!=0u)
            *(volatile uint32_t *)(uintptr_t)(record+0x30u)=stack;
        else case_boot_heap_free(stack);
    }
    if(record==0u)return (uint32_t)-1;
    *(volatile uint8_t *)(uintptr_t)(record+0x59u)=0u;
    case_boot_task_initialize((void (*)(void *))(uintptr_t)entry,
        (const char *)(uintptr_t)name,stack_words,(void *)(uintptr_t)arg,
        priority,task,record,0u);
    case_boot_task_register(record);
    return 1u;
}

uint32_t case_boot_transport_worker_static(uint32_t entry,uint32_t name,
    uint32_t stack_words,uint32_t arg,uint32_t priority,
    uint32_t stack_end,uint32_t stack_start)
{
    return case_boot_task_create((void (*)(void *))(uintptr_t)entry,
        (const char *)(uintptr_t)name,stack_words,(void *)(uintptr_t)arg,
        priority,stack_end,stack_start);
}
