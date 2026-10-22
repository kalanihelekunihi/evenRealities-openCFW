/* SPDX-License-Identifier: MIT
 * Native CASE 0x0800c48c/0x0800c4aa event object allocation and attachment.
 */
#include <stdint.h>
extern uint32_t case_boot_transport_heap_allocate(uint32_t bytes); /* 0xb3e8 */
extern void case_policy_task_list_initialize(uint32_t list); /* 0xbf94 */

/* Stock 0x0800C48C (case_boot_transport_event_allocate) */
uint32_t case_boot_transport_event_allocate(uint32_t descriptor)
{
    (void)descriptor; /* Native allocator ignores incoming R0. */
    uint32_t event=case_boot_transport_heap_allocate(32u);
    if(event!=0u){
        volatile uint32_t *state=(volatile uint32_t *)(uintptr_t)event;
        state[0u]=0u;
        case_policy_task_list_initialize(event+4u);
        *(volatile uint8_t *)(uintptr_t)(event+28u)=0u;
    }
    return event;
}

/* Stock 0x0800C4AA (case_boot_transport_event_create) */
uint32_t case_boot_transport_event_create(uint32_t storage)
{
    if(storage==0u){
        __asm__ volatile("cpsid i" ::: "memory");
        for(;;)__asm__ volatile("b ." ::: "memory");
    }
    volatile uint32_t *state=(volatile uint32_t *)(uintptr_t)storage;
    state[0u]=0u;
    case_policy_task_list_initialize(storage+4u);
    *(volatile uint8_t *)(uintptr_t)(storage+28u)=1u;
    return storage;
}
