/* SPDX-License-Identifier: MIT
 * Native CASE 0x0800aa48 callback task registration selector.
 */
#include <stdint.h>
extern uint32_t case_boot_transport_heap_allocate(uint32_t bytes); /* 0xb3e8 */
extern void case_boot_heap_free(uint32_t address); /* 0xc030 */
extern uint32_t case_boot_transport_register_dynamic(uint32_t callback,uint32_t priority,
    uint32_t mode,uint32_t context,uint32_t trampoline); /* 0xccc0 */
extern uint32_t case_boot_transport_register_static(uint32_t callback,uint32_t priority,
    uint32_t mode,uint32_t context,uint32_t trampoline,uint32_t storage); /* 0xccf2 */
extern void case_boot_transport_entry_8558(uint32_t task); /* stock Thumb 0x8559 */

/* Stock 0x0800AA48 (os_timer_or_thread_create_wrapper) */
uint32_t case_boot_transport_register(uint32_t callback,uint32_t mode,
                                      uint32_t flags,uint32_t storage)
{
    uint32_t ipsr;
    __asm__ volatile("mrs %0, ipsr" : "=r"(ipsr));
    if(ipsr!=0u || callback==0u)return 0u;
    uint32_t context=case_boot_transport_heap_allocate(8u);
    if(context==0u)return 0u;
    volatile uint32_t *ctx=(volatile uint32_t *)(uintptr_t)context;
    ctx[0u]=callback;
    ctx[1u]=flags;
    uint32_t selector=~0u;
    uint32_t entry=0u;
    if(storage!=0u){
        volatile const uint32_t *spec=(volatile const uint32_t *)(uintptr_t)storage;
        if(spec[0u]!=0u)entry=spec[0u];
        if(spec[2u]!=0u){
            if(spec[3u]>=44u)selector=1u;
        }else if(spec[3u]==0u)selector=0u;
    }else selector=0u;
    uint32_t task=0u;
    if(selector==1u){
        uint32_t buffer=*(volatile uint32_t *)(uintptr_t)(storage+8u);
        task=case_boot_transport_register_static(entry,1u,mode!=0u,context,
                                                  (uint32_t)(uintptr_t)case_boot_transport_entry_8558,buffer);
    }else if(selector==0u){
        task=case_boot_transport_register_dynamic(entry,1u,mode!=0u,context,
                                                   (uint32_t)(uintptr_t)case_boot_transport_entry_8558);
    }
    if(task==0u)case_boot_heap_free(context);
    return task;
}
