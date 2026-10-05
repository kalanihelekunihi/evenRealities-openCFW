/*************************************************************************************************/
/*!
 *  \file   wsf_os.c
 *
 *  \brief  Software foundation OS main module.
 *
 *  Copyright (c) 2009-2019 Arm Ltd. All Rights Reserved.
 *
 *  Copyright (c) 2019-2020 Packetcraft, Inc.
 *  
 *  Licensed under the Apache License, Version 2.0 (the "License");
 *  you may not use this file except in compliance with the License.
 *  You may obtain a copy of the License at
 *  
 *      http://www.apache.org/licenses/LICENSE-2.0
 *  
 *  Unless required by applicable law or agreed to in writing, software
 *  distributed under the License is distributed on an "AS IS" BASIS,
 *  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 *  See the License for the specific language governing permissions and
 *  limitations under the License.
 */
/*************************************************************************************************/

/* Stock-adapted reconstruction, not unchanged public WSF or private port.
 * Apollo state:10 handlers,8-bit events,64-byte control block. */
#include "wsf_radio.h"
#include <stddef.h>
_Static_assert(sizeof(void *)==4,"stock ARM32 WSF ABI");
_Static_assert(sizeof(opencfw_wsf_state_t)==64,"stock WSF state size");
_Static_assert(offsetof(opencfw_wsf_state_t,handler_event)==0x28,"stock byte events");
_Static_assert(offsetof(opencfw_wsf_state_t,queue_head)==0x34,"stock queue boundary");
_Static_assert(offsetof(opencfw_wsf_state_t,task_events)==0x3c,"stock task flags");
#define BYTE(a) (*(volatile uint8_t *)(uintptr_t)(a))
#define WORD(a) (*(volatile uint32_t *)(uintptr_t)(a))
#define STATE 0x20073230u
#define DEPTH 0x20075045u
#define TASK 0x20074ef0u
#define FLAGS BYTE(STATE+0x3cu)
#define EVENT(i) BYTE(STATE+0x28u+(i))
#define HANDLER(i) ((opencfw_wsf_handler_t)(uintptr_t)WORD(STATE+(i)*4u))
void opencfw_wsf_cs_enter(void)
{
    if(BYTE(DEPTH)==0u)__asm__ volatile("cpsid i" ::: "memory");
    BYTE(DEPTH)=(uint8_t)(BYTE(DEPTH)+1u);
}
void opencfw_wsf_cs_exit(void)
{
    BYTE(DEPTH)=(uint8_t)(BYTE(DEPTH)-1u);
    if(BYTE(DEPTH)==0u)__asm__ volatile("cpsie i" ::: "memory");
}
void opencfw_wsf_wake(void)
{
    if(WORD(TASK)==0u)return;
    if(opencfw_wsf_context_is_isr()==1u){
        int32_t higher_woken=0;
        if(opencfw_wsf_notify_isr(WORD(TASK),1u,&higher_woken)!=0 && higher_woken!=0)
            WORD(0xe000ed04u)=0x10000000u;
    }else if(opencfw_wsf_notify_task(WORD(TASK),1u)!=0){
        WORD(0xe000ed04u)=0x10000000u;
        __asm__ volatile("dsb sy\nisb sy" ::: "memory");
    }
}
void opencfw_wsf_set_event(uint32_t handler_id,uint32_t mask)
{
    opencfw_wsf_cs_enter();
    EVENT(handler_id&15u)=(uint8_t)(EVENT(handler_id&15u)|mask);
    FLAGS=(uint8_t)(FLAGS|4u);
    opencfw_wsf_cs_exit();
    opencfw_wsf_wake();
}
void opencfw_wsf_task_ready(uint32_t ignored_id,uint32_t mask)
{
    (void)ignored_id;
    opencfw_wsf_cs_enter();
    FLAGS=(uint8_t)(FLAGS|mask);
    opencfw_wsf_cs_exit();
    opencfw_wsf_wake();
}
uint32_t opencfw_wsf_ready_to_sleep(void){return FLAGS==0u;}
void opencfw_wsf_dispatch(void)
{
    opencfw_wsf_timer_update();
    while(FLAGS!=0u){
        opencfw_wsf_cs_enter();
        uint8_t flags=FLAGS;FLAGS=0;
        opencfw_wsf_cs_exit();
        if(flags&1u){
            uint8_t id;void *msg;
            while((msg=opencfw_wsf_msg_deq((void *)(uintptr_t)(STATE+0x34u),&id))!=NULL){
                HANDLER(id)(0u,msg);
                opencfw_wsf_msg_free(msg);
            }
        }
        if(flags&2u){
            void *timer;
            while((timer=opencfw_wsf_timer_expired(0u))!=NULL)
                HANDLER(*(uint8_t *)((uintptr_t)timer+12u))(0u,(void *)((uintptr_t)timer+8u));
        }
        if(flags&4u){
            for(uint32_t id=0;id<10u;id++){
                if(EVENT(id)!=0u && HANDLER(id)!=NULL){
                    opencfw_wsf_cs_enter();
                    uint8_t event=EVENT(id);EVENT(id)=0;
                    opencfw_wsf_cs_exit();
                    HANDLER(id)(event,NULL);
                }
            }
        }
    }
    opencfw_wsf_timer_update();
    if(opencfw_wsf_ready_to_sleep())
        opencfw_wsf_wait(WORD(TASK),1u,1u,0u,0xffffffffu);
}
/* Production adapter replaces the earlier event-submission test boundary. */
void opencfw_radio_scheduler_event(uint32_t id,uint32_t event)
{
    opencfw_wsf_set_event(id,event);
}
