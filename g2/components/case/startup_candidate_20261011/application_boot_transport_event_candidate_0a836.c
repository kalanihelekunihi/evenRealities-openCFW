/* SPDX-License-Identifier: MIT
 * Native 0x0800a836 event-object choose/create logic.
 */
#include <stdint.h>
extern uint32_t case_boot_transport_event_allocate(uint32_t); /* 0xc48c */
extern uint32_t case_boot_transport_event_create(uint32_t); /* 0xc4aa */
uint32_t case_boot_transport_event(uint32_t descriptor)
{
    uint32_t ipsr;
    __asm__ volatile("mrs %0, ipsr" : "=r"(ipsr));
    if(ipsr!=0u)return 0u;
    if(descriptor==0u)return case_boot_transport_event_allocate(0u);
    volatile uint32_t *d=(volatile uint32_t *)(uintptr_t)descriptor;
    uint32_t storage=d[2u];
    if(storage!=0u){
        if(d[3u]>=32u)return case_boot_transport_event_create(storage);
        return 0u;
    }
    if(d[3u]==0u)return case_boot_transport_event_allocate(descriptor);
    return 0u;
}
