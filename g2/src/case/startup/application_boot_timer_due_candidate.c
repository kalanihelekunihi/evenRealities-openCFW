/* SPDX-License-Identifier: MIT
 * CASE native 0xb024 timer-list insert decision and 0xb0a0 due callback.
 */
#include <stdint.h>
extern void case_policy_task_list_insert_sorted(uint32_t list,uint32_t link); /* 0xbfb0 */
extern void case_policy_task_unlink(uint32_t link); /* 0xbf2c */
extern uint32_t case_policy_task_event_send(uint32_t task,uint32_t op,uint32_t value,
                                            uint32_t option,uint32_t timeout); /* 0xcd80 */
static uint32_t rd(uint32_t a){return *(volatile uint32_t *)(uintptr_t)a;}
static void wr(uint32_t a,uint32_t v){*(volatile uint32_t *)(uintptr_t)a=v;}
static uint8_t rb(uint32_t a){return *(volatile uint8_t *)(uintptr_t)a;}
static void wb(uint32_t a,uint8_t v){*(volatile uint8_t *)(uintptr_t)a=v;}
static __attribute__((noreturn)) void native_fault(void)
{__asm__ volatile("cpsid i\n1: b 1b");__builtin_unreachable();}
static void invoke(uint32_t f,uint32_t timer){((void (*)(uint32_t))(uintptr_t)f)(timer);}
/* Stock 0x0800B024 (case_boot_timer_insert) */
uint32_t case_boot_timer_insert(uint32_t timer,uint32_t next,uint32_t now,uint32_t previous)
{
    wr(timer+4u,next);wr(timer+16u,timer);
    const uint32_t scheduler=0x20000164u;
    if(next<=now){
        if((now-previous)>=rd(timer+24u))return 1u;
        case_policy_task_list_insert_sorted(rd(scheduler+16u),timer+4u);
        return 0u;
    }
    if(now<previous && next>=previous)return 1u;
    case_policy_task_list_insert_sorted(rd(scheduler+12u),timer+4u);
    return 0u;
}
/* Stock 0x0800B0A0 (case_boot_timer_process_due) */
void case_boot_timer_process_due(uint32_t deadline,uint32_t now)
{
    uint32_t scheduler=0x20000164u;
    uint32_t timer=rd(rd(rd(scheduler+12u)+12u)+12u);
    case_policy_task_unlink(timer+4u);
    uint32_t state=timer+32u;
    if((rb(state+8u)&4u)!=0u){
        if(case_boot_timer_insert(timer,deadline+rd(timer+24u),now,deadline)!=0u){
            if(case_policy_task_event_send(timer,0u,deadline,0u,0u)==0u)native_fault();
        }
    }else wb(state+8u,rb(state+8u)&~1u);
    invoke(rd(timer+32u),timer);
}
