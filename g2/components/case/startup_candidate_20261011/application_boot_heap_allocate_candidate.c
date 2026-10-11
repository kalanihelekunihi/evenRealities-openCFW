/* SPDX-License-Identifier: MIT
 * Native CASE 0x0800b3e8 aligned heap allocation and 0x0800ae0c setup.
 */
#include <stdint.h>
extern void case_policy_task_sleep_enter(void); /* 0xc380 */
extern uint32_t case_policy_task_sleep_exit(void); /* 0xcc0c */
extern void case_boot_heap_insert(uint32_t block); /* 0xafcc */
static uint32_t rd(uint32_t a){return *(volatile uint32_t *)(uintptr_t)a;}
static void wr(uint32_t a,uint32_t v){*(volatile uint32_t *)(uintptr_t)a=v;}
static __attribute__((noreturn)) void native_fault(void)
{__asm__ volatile("cpsid i\n1: b 1b" ::: "memory");__builtin_unreachable();}

void case_boot_heap_initialize(void)
{
    uint32_t start=0x20001c88u;
    uint32_t span=3072u;
    if((start&7u)!=0u){
        uint32_t aligned=(start+7u)&~7u;
        span-=aligned-start;
        start=aligned;
    }
    uint32_t end=(start+span-8u)&~7u;
    wr(0x20000194u,start);
    wr(0x20000198u,0u);
    wr(0x2000017cu,end);
    wr(end,0u);
    wr(end+4u,0u);
    wr(start,end);
    wr(start+4u,end-start);
    wr(0x20000180u,end-start);
    wr(0x20000184u,end-start);
    wr(0x20000190u,0x80000000u);
}

uint32_t case_boot_transport_heap_allocate(uint32_t bytes)
{
    uint32_t result=0u;
    case_policy_task_sleep_enter();
    const uint32_t heap=0x2000017cu;
    if(rd(heap)==0u)case_boot_heap_initialize();
    uint32_t mask=rd(heap+20u);
    if((bytes&mask)!=0u || bytes==0u)goto done;
    uint32_t need=bytes+8u;
    if((need&7u)!=0u)need=(need+7u)&~7u;
    if((need&7u)!=0u)native_fault();
    if(need==0u || need>rd(heap+4u))goto done;
    uint32_t prior=0x20000194u;
    uint32_t block=rd(prior);
    while(rd(block+4u)<need && rd(block)!=0u){prior=block;block=rd(block);}
    if(block==rd(heap))goto done;
    result=rd(prior)+8u;
    wr(prior,rd(block));
    uint32_t available=rd(block+4u);
    if(available-need>16u){
        uint32_t rest=block+need;
        if((rest&7u)!=0u)native_fault();
        wr(rest+4u,available-need);
        wr(block+4u,need);
        case_boot_heap_insert(rest);
    }
    uint32_t taken=rd(block+4u);
    uint32_t free_bytes=rd(heap+4u)-taken;
    wr(heap+4u,free_bytes);
    if(free_bytes<rd(heap+8u))wr(heap+8u,free_bytes);
    wr(block+4u,taken|mask);
    wr(block,0u);
    wr(heap+12u,rd(heap+12u)+1u);
done:
    (void)case_policy_task_sleep_exit();
    if((result&7u)!=0u)native_fault();
    return result;
}
