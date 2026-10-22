/* SPDX-License-Identifier: MIT
 * Native CASE 0xc7a8 immediate scheduler message insertion.
 */
#include <stdint.h>
extern void case_policy_message_copy(uint32_t scheduler,const uint32_t *args,uint32_t mode); /* 0xad48 */
extern uint32_t case_boot_pool_wake_waiter(uint32_t list); /* 0xcba0 */
static uint32_t rd(uint32_t a){return *(volatile uint32_t *)(uintptr_t)a;}
static void wr(uint32_t a,uint32_t v){*(volatile uint32_t *)(uintptr_t)a=v;}
static __attribute__((noreturn)) void native_fault(void)
{__asm__ volatile("cpsid i\n1: b 1b");__builtin_unreachable();}
/* Stock 0x0800C7A8 (case_policy_task_message_special) */
uint32_t case_policy_task_message_special(uint32_t scheduler,const uint32_t *args,uint32_t notify,uint32_t mode,uint32_t meta)
{
    if(scheduler==0u)native_fault();
    if(meta==0u && rd(scheduler+64u)!=0u)native_fault();
    if(mode==2u && rd(scheduler+60u)!=1u)native_fault();
    uint32_t primask;
    __asm__ volatile("mrs %0, primask\ncpsid i":"=r"(primask)::"memory");
    uint32_t result=0u;
    if(rd(scheduler+56u)<rd(scheduler+60u) || mode==2u){
        int8_t sequence=*(volatile int8_t *)(uintptr_t)(scheduler+69u);
        case_policy_message_copy(scheduler,args,mode);
        if((int32_t)sequence+1!=0){
            *(volatile uint8_t *)(uintptr_t)(scheduler+69u)=(uint8_t)(sequence+1);
        }else if(rd(scheduler+36u)!=0u && case_boot_pool_wake_waiter(scheduler+36u)!=0u && notify!=0u){
            wr(notify,1u);
        }
        result=1u;
    }
    __asm__ volatile("msr primask, %0"::"r"(primask):"memory");
    return result;
}
