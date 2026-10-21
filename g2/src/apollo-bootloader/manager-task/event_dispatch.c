/* SPDX-License-Identifier: MIT. Stock42e644/42e686/42e6f4. */
#include "event_dispatch.h"
extern int32_t opencfw_provider_416920(uintptr_t,void *,uintptr_t,uint32_t);
extern int32_t opencfw_provider_4168a2(uintptr_t,const void *,uint32_t,uint32_t);
extern int32_t opencfw_provider_4166aa(uintptr_t,uint32_t);
extern int32_t opencfw_provider_416710(uintptr_t);
extern int32_t opencfw_provider_41649a(uintptr_t,uint32_t);
extern uint32_t opencfw_provider_4160e8(void);
extern void opencfw_bl_kernel_enter(void);
extern void opencfw_bl_kernel_exit(void);
extern void opencfw_provider_4176ce(uint32_t,const char *,const char *,const char *,uint32_t,const char *,...);
#define WORD(a) (*(volatile uint32_t *)(uintptr_t)(a))
static const char module[]="evtloop";
static const char file[]="D:\\01_workspace\\s200_ap510b_iar_git\\framework\\fw_event_loop\\fw_event_loop.c";
void opencfw_boot_event_thread(void *argument) {
    (void)argument;
    opencfw_boot_event_message message;
    for (;;) {
        int32_t status=opencfw_provider_416920(WORD(0x200270ec),&message,0,UINT32_MAX);
        if (!status) {
            void (*callback)(uint32_t)=(void (*)(uint32_t))(uintptr_t)message.callback_address;
            callback(message.argument);
        } else opencfw_provider_4176ce(1,module,file,"fw_evt_loop_task",0x8c,
            "[fw_evt_loop_task]app treat event invalid status:%d",status);
    }
}
void opencfw_boot_event_enqueue(uint32_t callback,uint32_t argument,uint32_t timeout) {
    if (!WORD(0x200270f0)) {
        opencfw_provider_4176ce(1,module,file,"fw_evt_loop_push",0x96,
            "[fw_evt_loop_push]fw_evt_loop_thread_id is NULL");
        return;
    }
    opencfw_boot_event_message message={argument,callback};
    if (WORD(0x200270ec)) {
        int32_t status=opencfw_provider_4168a2(WORD(0x200270ec),&message,0,timeout);
        if (status)opencfw_provider_4176ce(1,module,file,"fw_evt_loop_push",0xa0,
            "[fw_evt_loop_push]fw_event_push error:0x%x",(uint32_t)status);
    }
}
void opencfw_boot_event_timer_callback(uint32_t argument) {
    uint32_t shortest=UINT32_MAX,elapsed;
    opencfw_bl_kernel_enter();elapsed=WORD(0x20027100);opencfw_bl_kernel_exit();
    if ((argument&0xff000000)==0xff000000)elapsed=argument&0xffffff;
    const char *function="fw_evt_loop_timer_callback";
    if (opencfw_provider_4166aa(WORD(0x200270f4),UINT32_MAX))
        opencfw_provider_4176ce(1,module,file,function,0xb8,
            "[fw_evt_loop_timer_callback]fw_event lock fail");
    volatile uint32_t *const table=(volatile uint32_t *)(uintptr_t)0x20025ff0;
    for (uint32_t i=0;i<64;i++) {
        if (!table[i])continue;
        uint32_t remaining=table[128+i];
        table[128+i]=elapsed>=remaining?0:remaining-elapsed;
        if (!table[128+i]) {
            uint32_t callback=table[i];table[i]=0;
            opencfw_boot_event_enqueue(callback,table[64+i],1);
        }
    }
    for (uint32_t i=0;i<64;i++)
        if (table[i] && table[128+i]<shortest)shortest=table[128+i];
    if (opencfw_provider_416710(WORD(0x200270f4)))
        opencfw_provider_4176ce(1,module,file,function,0xd5,
            "[fw_evt_loop_timer_callback]fw_event unlock fail");
    /* Preserve stock's guard exactly: it excludes7fffffff, notffffffff. */
    if (shortest!=0x7fffffff && shortest!=0) {
        opencfw_bl_kernel_enter();WORD(0x20027100)=shortest;opencfw_bl_kernel_exit();
        int32_t status=opencfw_provider_41649a(WORD(0x200270f8),shortest);
        if (status)opencfw_provider_4176ce(1,module,file,function,0xe1,
            "osTimerStart  next_delay %d stat = %d",(int32_t)shortest,status);
        WORD(0x200270fc)=opencfw_provider_4160e8();
    }
}
