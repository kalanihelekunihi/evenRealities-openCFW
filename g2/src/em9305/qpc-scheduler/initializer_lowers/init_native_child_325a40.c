#include <stdint.h>

/* Native 0x325a40..0x325a68: allocate a 4-byte message {u16 handle,
 * u8 8, u8 status} for the record's handle byte and send it to the task
 * at 0x805b18. Returns 0 if allocation fails. */
extern uintptr_t opencfw_em9305_wsf_event_allocate(uint32_t length);
extern uint32_t opencfw_em9305_wsf_task_message_send(uint32_t task, uintptr_t message);

uint32_t opencfw_em9305_child_325a40(uintptr_t record, uint32_t status)
{
    uintptr_t message=opencfw_em9305_wsf_event_allocate(4u);
    if(message==0u)return 0u;
    uint32_t task=*(volatile uint8_t *)(uintptr_t)0x805b18u;
    uint32_t handle=*(volatile uint8_t *)(record+1u);
    *(volatile uint8_t *)(message+3u)=(uint8_t)status;
    *(volatile uint16_t *)message=(uint16_t)handle;
    *(volatile uint8_t *)(message+2u)=8u;
    return opencfw_em9305_wsf_task_message_send(task,message);
}
