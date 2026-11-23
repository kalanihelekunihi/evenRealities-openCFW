#include <stdint.h>
#include "em9305_ram.h"

/* Native 0x31d128..0x31d150: send event 17 for the record's id (+2) with
 * one status byte to the task at ((uintptr_t)&em9305_ram_805af0 + 0x28u). Returns 0 when no 4-byte
 * message could be allocated. */
extern uintptr_t opencfw_em9305_wsf_event_allocate(uint32_t);
extern uint32_t opencfw_em9305_wsf_task_message_send(uint32_t,uintptr_t);

uint32_t opencfw_em9305_dispatch_event_send_31d128(uintptr_t record,uint32_t status)
{
    uintptr_t message=opencfw_em9305_wsf_event_allocate(4u);
    if(message==0u) return 0u;
    uint32_t task=em9305_ram_805af0.u8_805b18;
    uint32_t id=*(volatile uint8_t *)(record+2u);
    *(volatile uint8_t *)(message+3u)=(uint8_t)status;
    *(volatile uint16_t *)message=(uint16_t)id;
    *(volatile uint8_t *)(message+2u)=17u;
    return opencfw_em9305_wsf_task_message_send(task,message);
}
