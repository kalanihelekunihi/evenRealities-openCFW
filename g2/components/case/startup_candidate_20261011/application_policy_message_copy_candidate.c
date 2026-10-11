/* SPDX-License-Identifier: MIT
 * Native CASE 0xad48 ring payload copy and queue count update.
 */
#include <stdint.h>
extern uint32_t case_policy_task_notify_resume(uint32_t task); /* 0xcb38 */
static uint32_t rd(uint32_t a){return *(volatile uint32_t *)(uintptr_t)a;}
static void wr(uint32_t a,uint32_t v){*(volatile uint32_t *)(uintptr_t)a=v;}
static void copy_bytes(uint32_t destination,const uint8_t *source,uint32_t count)
{for(uint32_t i=0u;i<count;++i)*(volatile uint8_t *)(uintptr_t)(destination+i)=source[i];}
uint32_t case_policy_message_copy(uint32_t queue,const uint32_t *args,uint32_t mode)
{
    uint32_t count=rd(queue+56u),width=rd(queue+64u),result=0u;
    if(width!=0u){
        if(mode!=0u){
            uint32_t destination=rd(queue+12u);
            copy_bytes(destination,(const uint8_t *)args,width);
            uint32_t next=destination-width;
            if(next<rd(queue))next=rd(queue+8u)-width;
            wr(queue+12u,next);
            if(mode==2u && count!=0u)--count;
        }else{
            uint32_t destination=rd(queue+4u);
            copy_bytes(destination,(const uint8_t *)args,width);
            uint32_t next=destination+width;
            if(next>=rd(queue+8u))next=rd(queue);
            wr(queue+4u,next);
        }
    }else if(rd(queue)==0u){
        result=case_policy_task_notify_resume(rd(queue+8u));
        wr(queue+8u,0u);
    }
    wr(queue+56u,count+1u);
    return result;
}
