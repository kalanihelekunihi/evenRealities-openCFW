/* SPDX-License-Identifier: MIT
 * CASE native 0x0800b0fc timer command queue drain.
 */
#include <stdint.h>
extern uint32_t case_boot_timer_command_receive(uint32_t queue,uint32_t *message,uint32_t wait); /* 0xc83a */
extern void case_policy_task_unlink(uint32_t link); /* 0xbf2c */
extern uint32_t case_boot_timer_now(uint32_t *overflow); /* 0xb284 */
extern uint32_t case_boot_timer_insert(uint32_t timer,uint32_t next,uint32_t now,uint32_t previous); /* 0xb024 */
extern uint32_t case_policy_task_event_send(uint32_t task,uint32_t op,uint32_t value,uint32_t option,uint32_t timeout); /* 0xcd80 */
extern void case_boot_heap_free(uint32_t address); /* 0xc030 */
static uint32_t rd(uint32_t a){return *(volatile uint32_t *)(uintptr_t)a;}
static void wr(uint32_t a,uint32_t v){*(volatile uint32_t *)(uintptr_t)a=v;}
static uint8_t rb(uint32_t a){return *(volatile uint8_t *)(uintptr_t)a;}
static void wb(uint32_t a,uint8_t v){*(volatile uint8_t *)(uintptr_t)a=v;}
static __attribute__((noreturn)) void native_fault(void)
{__asm__ volatile("cpsid i\n1: b 1b");__builtin_unreachable();}
/* Stock 0x0800B0FC (prvTimerTask) */
void case_boot_timer_expired(void)
{
    uint32_t message[4];
    while(case_boot_timer_command_receive(rd(0x20000164u),message,0u)!=0u){
        uint32_t command=message[0];
        if((int32_t)command<0){
            ((void (*)(void *,uint32_t))(uintptr_t)message[1])((void *)(uintptr_t)message[2],message[3]);
            continue;
        }
        uint32_t timer=message[2];
        if(rd(timer+20u)!=0u)case_policy_task_unlink(timer+4u);
        uint32_t overflow,now=case_boot_timer_now(&overflow);
        (void)overflow;
        if(command>=10u)continue;
        if(command==3u || command==8u){
            wb(timer+40u,rb(timer+40u)&~1u);
            continue;
        }
        if(command==4u || command==9u){
            wb(timer+40u,rb(timer+40u)|1u);
            uint32_t period=message[1];
            wr(timer+24u,period);
            if(period==0u)native_fault();
            (void)case_boot_timer_insert(timer,period+now,now,now);
            continue;
        }
        if(command==5u){
            if((rb(timer+40u)&2u)==0u)case_boot_heap_free(timer);
            else wb(timer+40u,rb(timer+40u)&~1u);
            continue;
        }
        wb(timer+40u,rb(timer+40u)|1u);
        uint32_t next=message[1]+rd(timer+24u);
        if(case_boot_timer_insert(timer,next,now,message[1])==0u)continue;
        ((void (*)(uint32_t))(uintptr_t)rd(timer+32u))(timer);
        if((rb(timer+40u)&4u)!=0u)
            if(case_policy_task_event_send(timer,0u,next,0u,0u)==0u)native_fault();
    }
}
