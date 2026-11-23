#include <stdint.h>
#include "em9305_ram.h"

/* Native 0x325edc..0x325f0a: send a 4-byte WSF message {id, 7, value} to the
 * handler at ((uintptr_t)&em9305_ram_805af0 + 0x28u); id is byte +16 of the record, or 0xff without one.
 * Returns 0 when no message buffer is available. */
extern uintptr_t opencfw_em9305_wsf_event_allocate(uint32_t);
extern uint32_t opencfw_em9305_wsf_task_message_send(uint32_t,uintptr_t);

uint32_t opencfw_em9305_child_325edc(uintptr_t record, uint32_t value)
{
    uintptr_t message = opencfw_em9305_wsf_event_allocate(4u);
    if (message == 0u) return 0u;
    uint32_t id = record != 0u ? *(volatile uint8_t *)(record + 16u) : 0xffu;
    uint32_t handler = em9305_ram_805af0.u8_805b18;
    *(volatile uint8_t *)(message + 3u) = (uint8_t)value;
    *(volatile uint16_t *)message = (uint16_t)id;
    *(volatile uint8_t *)(message + 2u) = 7u;
    return opencfw_em9305_wsf_task_message_send(handler, message);
}
