/* SPDX-License-Identifier: MIT
 * CASE native 0x0800b2b0 timer-list wrap processing.
 */
#include <stdint.h>
extern void case_policy_task_unlink(uint32_t link); /* 0xbf2c */
extern void case_policy_task_list_insert_sorted(uint32_t list,uint32_t link); /* 0xbfb0 */
extern uint32_t case_policy_task_event_send(uint32_t timer,uint32_t op,uint32_t value,
                                            uint32_t option,uint32_t timeout); /* 0xcd80 */
static uint32_t rd(uint32_t a){return *(volatile uint32_t *)(uintptr_t)a;}
static void wr(uint32_t a,uint32_t v){*(volatile uint32_t *)(uintptr_t)a=v;}
static uint8_t rb(uint32_t a){return *(volatile uint8_t *)(uintptr_t)a;}
static __attribute__((noreturn)) void native_fault(void)
{__asm__ volatile("cpsid i\n1: b 1b");__builtin_unreachable();}
void case_boot_timer_handle_wrap(void)
{
    uint32_t scheduler=0x20000164u;
    while(rd(rd(scheduler+12u))!=0u){
        uint32_t list=rd(scheduler+12u);
        uint32_t entry=rd(list+12u);
        uint32_t tick=rd(entry);
        uint32_t timer=rd(entry+12u);
        case_policy_task_unlink(timer+4u);
        ((void (*)(uint32_t))(uintptr_t)rd(timer+32u))(timer);
        if((rb(timer+40u)&4u)!=0u){
            uint32_t next=tick+rd(timer+24u);
            if(next>tick){
                wr(timer+4u,next);wr(timer+16u,timer);
                case_policy_task_list_insert_sorted(rd(scheduler+12u),timer+4u);
            }else if(case_policy_task_event_send(timer,0u,tick,0u,0u)==0u)native_fault();
        }
    }
    uint32_t first=rd(scheduler+12u),second=rd(scheduler+16u);
    wr(scheduler+12u,second);wr(scheduler+16u,first);
}
