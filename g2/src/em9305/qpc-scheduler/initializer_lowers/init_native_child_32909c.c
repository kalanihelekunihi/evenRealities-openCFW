#include <stdint.h>
#include "em9305_ram.h"

/* Native 0x32909c..0x3290c4: send a 4-byte WSF message {handle, 16, value}
 * for the packet's handle (byte +2) to the handler at ((uintptr_t)&em9305_ram_805af0 + 0x28u). Returns 0
 * when no message buffer is available. */
extern uintptr_t opencfw_em9305_wsf_event_allocate(uint32_t);
extern uint32_t opencfw_em9305_wsf_task_message_send(uint32_t,uintptr_t);

uint32_t opencfw_em9305_child_32909c(uintptr_t packet, uint32_t value)
{
    uintptr_t message = opencfw_em9305_wsf_event_allocate(4u);
    if (message == 0u) return 0u;
    uint32_t handle = *(volatile uint8_t *)(packet + 2u);
    uint32_t handler = em9305_ram_805af0.u8_805b18;
    *(volatile uint8_t *)(message + 3u) = (uint8_t)value;
    *(volatile uint16_t *)message = (uint16_t)handle;
    *(volatile uint8_t *)(message + 2u) = 16u;
    return opencfw_em9305_wsf_task_message_send(handler, message);
}
