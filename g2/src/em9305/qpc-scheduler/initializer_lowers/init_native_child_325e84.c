#include <stdint.h>
#include "em9305_ram.h"

/* Native 0x325e84..0x325eb2: allocate a 4-byte message {u16 handle,
 * u8 9, u8 status} (handle from +16 of the connection, 0xff when none)
 * and send it to the task at ((uintptr_t)&em9305_ram_805af0 + 0x28u). Returns 0 if allocation fails. */
extern uintptr_t opencfw_em9305_wsf_event_allocate(uint32_t length);
extern uint32_t opencfw_em9305_wsf_task_message_send(uint32_t task, uintptr_t message);

uint32_t opencfw_em9305_child_325e84(uintptr_t connection, uint32_t status)
{
    uintptr_t message=opencfw_em9305_wsf_event_allocate(4u);
    if(message==0u)return 0u;
    uint32_t handle=connection!=0u?*(volatile uint8_t *)(connection+16u):0xffu;
    uint32_t task=em9305_ram_805af0.u8_805b18;
    *(volatile uint8_t *)(message+3u)=(uint8_t)status;
    *(volatile uint16_t *)message=(uint16_t)handle;
    *(volatile uint8_t *)(message+2u)=9u;
    return opencfw_em9305_wsf_task_message_send(task,message);
}
