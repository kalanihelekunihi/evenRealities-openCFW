/* SPDX-License-Identifier: MIT. Stock42e53c event-loop resource initialization. */
#include <stdint.h>
#include <stddef.h>
extern uintptr_t opencfw_provider_416816(uint32_t,uint32_t,const uint32_t *);
extern uintptr_t opencfw_provider_4163b2(uintptr_t,uint32_t,uintptr_t,const uint32_t *);
extern uintptr_t opencfw_provider_416610(const uint32_t *);
extern void opencfw_provider_416200(uintptr_t);
extern uintptr_t opencfw_provider_4160fe(uintptr_t,uintptr_t,const uint32_t *);
extern void opencfw_provider_4176ce(uint32_t,const char *,const char *,const char *,uint32_t,const char *,...);
#define WORD(a) (*(volatile uint32_t *)(uintptr_t)(a))
__attribute__((section(".event_queue_name"),used))
const char opencfw_boot_event_queue_name[]="fw_evt_loop_mesq";
__attribute__((section(".event_mutex_name"),used))
const char opencfw_boot_event_mutex_name[]="fw_evt_loop_mutex";
__attribute__((section(".event_thread_name"),used))
const char opencfw_boot_event_thread_name[]="evt_loop";
static const uint32_t queue_attr[6]={0x433b3c,0,0x20026d00,80,0x200268f8,120};
static const uint32_t timer_attr[4]={0x433b50,0,0x20026eac,44};
static const uint32_t mutex_attr[4]={0x433b50,0,0x20026d50,80};
static const uint32_t thread_attr[9]={0x433f68,0,0x20026a50,112,0x200f3800,3072,38,0,0};
static void failed(uint32_t line,const char *message) {
    opencfw_provider_4176ce(1,"evtloop",
        "D:\\01_workspace\\s200_ap510b_iar_git\\framework\\fw_event_loop\\fw_event_loop.c",
        "fw_evt_loop_init",line,message);
}
void opencfw_provider_42e53c(void) {
    if (!WORD(0x200270ec)) {
        WORD(0x200270ec)=opencfw_provider_416816(15,8,queue_attr);
        if (!WORD(0x200270ec))failed(0x58,"[fw_evt_loop_init]osMessageQueueNew, fail");
    }
    if (!WORD(0x200270f8)) {
        WORD(0x200270f8)=opencfw_provider_4163b2(0x42e6f5,0,0,timer_attr);
        if (!WORD(0x200270f8))failed(0x61,"[fw_evt_loop_init]osTimerNew, failed");
    }
    if (!WORD(0x200270f4)) {
        WORD(0x200270f4)=opencfw_provider_416610(mutex_attr);
        if (!WORD(0x200270f4))failed(0x6a,"Warning: failed to Create fw_evt_loop_mutex_id");
    }
    if (WORD(0x200270f0)) {
        opencfw_provider_416200(WORD(0x200270f0));
        WORD(0x200270f0)=0;
    }
    if (!WORD(0x200270f0)) {
        WORD(0x200270f0)=opencfw_provider_4160fe(0x42e645,0,thread_attr);
        if (!WORD(0x200270f0))failed(0x79,"[fw_evt_loop_init]osThreadNew, fail");
    }
}
