#include <stdint.h>
#include "em9305_ram.h"

/* Native 0x329064..0x32909a: when the record has an attached object
 * (+180), send a 6-byte message 14 to the task at ((uintptr_t)&em9305_ram_805af0 + 0x28u) carrying the
 * object's id byte (+1) as a halfword, the status and the record byte +2. */
extern uintptr_t opencfw_em9305_wsf_event_allocate(uint32_t bytes);
extern uint32_t opencfw_em9305_wsf_task_message_send(uint32_t handler,
                                                     uintptr_t message);

uint32_t opencfw_em9305_child_329064(uintptr_t record,uint32_t status)
{
    if(*(volatile uint32_t *)(record+180u)==0u)return 0u;
    uintptr_t message=opencfw_em9305_wsf_event_allocate(6u);
    if(message==0u)return 0u;
    uintptr_t object=*(volatile uint32_t *)(record+180u);
    uint32_t handler=*(volatile uint8_t *)((uintptr_t)&em9305_ram_805af0 + 0x28u);
    uint32_t kind=*(volatile uint8_t *)(record+2u);
    uint32_t id=*(volatile uint8_t *)(object+1u);
    *(volatile uint8_t *)(message+3u)=(uint8_t)status;
    *(volatile uint8_t *)(message+4u)=(uint8_t)kind;
    *(volatile uint16_t *)message=(uint16_t)id;
    *(volatile uint8_t *)(message+2u)=14u;
    return opencfw_em9305_wsf_task_message_send(handler,message);
}
