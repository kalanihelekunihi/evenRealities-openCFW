#include <stdint.h>

/* Native 0x326108..0x32613c: send a 4-byte WSF message {index, 13, value}
 * for a 784-byte record in the table at 0x803d78 to the handler at
 * 0x805b18. Returns 0 when no message buffer is available. */
extern uintptr_t opencfw_em9305_wsf_event_allocate(uint32_t);
extern uint32_t opencfw_em9305_wsf_task_message_send(uint32_t,uintptr_t);

uint32_t opencfw_em9305_child_326108(uintptr_t record, uint32_t value)
{
    uintptr_t message = opencfw_em9305_wsf_event_allocate(4u);
    if (message == 0u) return 0u;
    uint8_t index = (uint8_t)((int32_t)(record - 0x803d78u) / 784);
    *(volatile uint8_t *)(message + 3u) = (uint8_t)value;
    *(volatile uint8_t *)(message + 2u) = 13u;
    uint32_t handler = *(volatile uint8_t *)(uintptr_t)0x805b18u;
    *(volatile uint16_t *)message = index;
    return opencfw_em9305_wsf_task_message_send(handler, message);
}
