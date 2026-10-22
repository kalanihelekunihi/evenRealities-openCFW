/* SPDX-License-Identifier: MIT
 * CASE 0x0800c4de task-context event notification. Task value is word zero;
 * the circular waiter list has its sentinel at task+12 and head at task+16.
 * bits and high control bits are evaluated as native c4de does.
 */
#include <stdint.h>
extern void case_policy_task_sleep_enter(void); /* 0xc380 */
extern void case_unblock_waiter(void *event_item,uint32_t event_bits); /* 0xc1cc */
extern uint32_t case_policy_task_sleep_exit(void); /* 0xcc0c */
static uint32_t rd(uint32_t a){return *(volatile uint32_t *)(uintptr_t)a;}
static void wr(uint32_t a,uint32_t v){*(volatile uint32_t *)(uintptr_t)a=v;}
static __attribute__((noreturn)) void native_fault(void)
{__asm__ volatile("cpsid i\n1: b 1b");__builtin_unreachable();}
/* Stock 0x0800C4DE (case_event_group_set_bits) */
int32_t case_boot_sensor_finish_signal_task(uint32_t task,uint32_t bits)
{
    if(task==0u||(bits>>24)!=0u)native_fault();
    uint32_t clear=0u;
    uint32_t sentinel=task+12u;
    case_policy_task_sleep_enter();
    wr(task,rd(task)|bits);
    for(uint32_t item=rd(task+16u);item!=sentinel;){
        uint32_t next=rd(item+4u);
        uint32_t option=rd(item);
        uint32_t mask=option&0x00ffffffu;
        uint32_t matched=(option&0x04000000u)?
            ((mask&~rd(task))==0u):((mask&rd(task))!=0u);
        if(matched){
            if(option&0x01000000u)clear|=mask;
            case_unblock_waiter((void *)(uintptr_t)item,rd(task)|0x02000000u);
        }
        item=next;
    }
    wr(task,rd(task)&~clear);
    (void)case_policy_task_sleep_exit();
    return (int32_t)rd(task);
}
