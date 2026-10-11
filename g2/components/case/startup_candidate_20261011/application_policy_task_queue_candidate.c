/* SPDX-License-Identifier: MIT
 * Native CASE 0xabb0, 0xbf2c, 0xbfe2 scheduler queue operations.
 */
#include <stdint.h>
extern void case_policy_task_list_insert_sorted(uint32_t list,uint32_t link); /* 0xbfb0 */
static uint32_t rd(uint32_t a){return *(volatile uint32_t *)(uintptr_t)a;}
static void wr(uint32_t a,uint32_t v){*(volatile uint32_t *)(uintptr_t)a=v;}
static __attribute__((noreturn)) void native_fault(void)
{__asm__ volatile("cpsid i\n1: b 1b");__builtin_unreachable();}
void case_policy_task_list_initialize(uint32_t list)
{
    uint32_t sentinel=list+8u;
    wr(list+4u,sentinel);wr(sentinel,0xffffffffu);
    wr(list+12u,sentinel);wr(list+16u,sentinel);wr(list,0u);
}
uint32_t case_policy_task_valid(uint32_t task)
{
    if(task==0u)native_fault();
    return rd(task+20u)==0x200014a4u && rd(task+40u)==0u;
}

__attribute__((noinline)) void case_policy_task_unlink(uint32_t link)
{
    uint32_t list=rd(link+16u),prev=rd(link+4u),next=rd(link+8u);
    wr(prev+8u,next);wr(next+4u,prev);
    if(rd(list+4u)==link)wr(list+4u,next);
    wr(link+16u,0u);wr(list,rd(list)-1u);
}
__attribute__((noinline)) void case_policy_task_list_insert(uint32_t list,uint32_t link)
{
    uint32_t first=rd(list+4u),second=rd(first+8u);
    wr(link+4u,first);wr(link+8u,second);
    wr(second+4u,link);wr(first+8u,link);
    wr(link+16u,list);wr(list,rd(list)+1u);
}
__attribute__((noinline)) void case_policy_task_list_insert_sorted(uint32_t list,uint32_t link)
{
    uint32_t key=rd(link);
    uint32_t prior;
    if(key==0xffffffffu)prior=rd(list+16u);
    else{
        prior=list+8u;
        while(rd(rd(prior+4u))<=key)prior=rd(prior+4u);
    }
    uint32_t next=rd(prior+4u);
    wr(link+4u,next);wr(next+8u,link);
    wr(link+8u,prior);wr(prior+4u,link);
    wr(link+16u,list);wr(list,rd(list)+1u);
}
void case_policy_task_sleep_enqueue(uint32_t ticks,uint32_t mode)
{
    uint32_t scheduler=0x20000128u;
    uint32_t current=rd(scheduler);
    uint32_t now=rd(scheduler+12u);
    case_policy_task_unlink(current+4u);
    if(ticks==0xffffffffu && mode!=0u){
        case_policy_task_list_insert(0x200014a4u,current+4u);
        return;
    }
    uint32_t deadline=now+ticks;
    wr(current+4u,deadline);
    uint32_t list=(deadline<now)?rd(scheduler+56u):rd(scheduler+52u);
    case_policy_task_list_insert_sorted(list,current+4u);
    if(deadline>=now && deadline<rd(scheduler+40u))wr(scheduler+40u,deadline);
}
