#include <stdint.h>

/* Native 0x32bb40..0x32bb9a: for each configured record (config byte 12)
 * ask the query hook at *0x801310 whether it needs a channel-class update;
 * if so send event 14 {record, a, b} to the task at 0x805b18. Returns 0x0c
 * if a 12-byte message could not be allocated, else 0. The stock call
 * leaves the hook address in r1. */
extern uintptr_t opencfw_em9305_wsf_event_allocate(uint32_t);
extern uint32_t opencfw_em9305_wsf_task_message_send(uint32_t,uintptr_t);

uint32_t opencfw_em9305_callback_32bb40(uint32_t first,uint32_t second)
{
    for(uint32_t index=0u;;++index) {
        uintptr_t config=*(volatile uint32_t *)(uintptr_t)0x805cacu;
        if((uint16_t)index>=*(volatile uint8_t *)(config+0xcu)) return 0u;
        uintptr_t query=*(volatile uint32_t *)(uintptr_t)0x801310u;
        if(((uint32_t (*)(uint32_t,uintptr_t))query)((uint8_t)index,query)==0u) continue;
        uintptr_t message=opencfw_em9305_wsf_event_allocate(12u);
        if(message==0u) return 0x0cu;
        *(volatile uint16_t *)(message+2u)=14u;
        uint32_t task=*(volatile uint8_t *)(uintptr_t)0x805b18u;
        *(volatile uint32_t *)(message+4u)=first;
        *(volatile uint32_t *)(message+8u)=second;
        *(volatile uint16_t *)message=(uint16_t)index;
        (void)opencfw_em9305_wsf_task_message_send(task,message);
    }
}
