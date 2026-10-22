/* SPDX-License-Identifier: MIT
 * Native CASE 0x0800a93c worker task descriptor selector.
 */
#include <stdint.h>
extern uint32_t case_boot_transport_worker_dynamic(uint32_t entry,uint32_t trampoline,
    uint32_t stack_words,uint32_t mode,uint32_t priority,uint32_t *task); /* 0xc9a8 */
extern uint32_t case_boot_transport_worker_static(uint32_t entry,uint32_t trampoline,
    uint32_t stack_words,uint32_t mode,uint32_t priority,
    uint32_t task_storage,uint32_t stack_storage); /* 0xca06 */

/* Stock 0x0800A93C (os_timer_or_thread_create_wrapper) */
uint32_t case_boot_transport_worker(uint32_t entry,uint32_t mode,uint32_t storage)
{
    uint32_t ipsr;
    __asm__ volatile("mrs %0, ipsr" : "=r"(ipsr));
    if(ipsr!=0u || entry==0u)return 0u;
    uint32_t trampoline=0u,priority=24u,stack_words=128u;
    uint32_t selector=0u;
    if(storage!=0u){
        volatile const uint32_t *spec=(volatile const uint32_t *)(uintptr_t)storage;
        trampoline=spec[0u];
        if(spec[6u]!=0u)priority=spec[6u];
        if(priority==0u || priority>56u || (spec[1u]&1u)!=0u)return 0u;
        if(spec[5u]!=0u)stack_words=spec[5u]>>2u;
        selector=~0u;
        if(spec[2u]!=0u){
            if(spec[3u]>=92u && spec[4u]!=0u && spec[5u]!=0u)selector=1u;
        }else if(spec[3u]==0u && spec[4u]==0u)selector=0u;
    }
    if(selector==1u){
        volatile const uint32_t *spec=(volatile const uint32_t *)(uintptr_t)storage;
        return case_boot_transport_worker_static(entry,trampoline,stack_words,mode,
            priority,spec[4u],spec[2u]);
    }
    if(selector==0u){
        uint32_t task=0u;
        if(case_boot_transport_worker_dynamic(entry,trampoline,(uint16_t)stack_words,
                                              mode,priority,&task)==1u)return task;
    }
    return 0u;
}
