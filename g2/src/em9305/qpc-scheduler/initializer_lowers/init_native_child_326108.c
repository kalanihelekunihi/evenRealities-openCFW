#include <stdint.h>
#include "em9305_ram.h"

/* Native 0x326108..0x32613c: send a 4-byte WSF message {index, 13, value}
 * for a 784-byte record in the table at ((uintptr_t)&em9305_ram_803d58 + 0x20u) to the handler at
 * ((uintptr_t)&em9305_ram_805af0 + 0x28u). Returns 0 when no message buffer is available. */
extern uintptr_t opencfw_em9305_wsf_event_allocate(uint32_t);
extern uint32_t opencfw_em9305_wsf_task_message_send(uint32_t,uintptr_t);

uint32_t opencfw_em9305_child_326108(uintptr_t record, uint32_t value)
{
    uintptr_t message = opencfw_em9305_wsf_event_allocate(4u);
    if (message == 0u) return 0u;
    uint8_t index = (uint8_t)((int32_t)(record - ((uintptr_t)&em9305_ram_803d58 + 0x20u)) / 784);
    *(volatile uint8_t *)(message + 3u) = (uint8_t)value;
    *(volatile uint8_t *)(message + 2u) = 13u;
    uint32_t handler = em9305_ram_805af0.u8_805b18;
    *(volatile uint16_t *)message = index;
    return opencfw_em9305_wsf_task_message_send(handler, message);
}
