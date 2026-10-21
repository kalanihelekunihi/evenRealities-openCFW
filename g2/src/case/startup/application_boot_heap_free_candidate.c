/* SPDX-License-Identifier: MIT
 * Native CASE 0x0800c030 heap-block release and accounting.
 */
#include <stdint.h>
extern void case_policy_task_sleep_enter(void);
extern uint32_t case_policy_task_sleep_exit(void);
extern void case_boot_heap_insert(uint32_t block); /* 0xafcc */
static __attribute__((noreturn)) void native_fault(void)
{__asm__ volatile("cpsid i\n1: b 1b");__builtin_unreachable();}
static uint32_t rd(uint32_t a){return *(volatile uint32_t *)(uintptr_t)a;}
static void wr(uint32_t a,uint32_t v){*(volatile uint32_t *)(uintptr_t)a=v;}
void case_boot_heap_free(uint32_t address)
{
    if(address==0u)return;
    uint32_t block=address-8u;
    uint32_t heap=0x2000017cu;
    uint32_t meta=rd(block+4u),mask=rd(heap+20u);
    if((meta&mask)==0u || rd(block)!=0u)native_fault();
    meta&=~mask;wr(block+4u,meta);
    case_policy_task_sleep_enter();
    wr(heap+4u,rd(heap+4u)+rd(block+4u));
    case_boot_heap_insert(block);
    wr(heap+16u,rd(heap+16u)+1u);
    (void)case_policy_task_sleep_exit();
}
