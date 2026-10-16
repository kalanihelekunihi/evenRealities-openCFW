#include <stdint.h>

extern uintptr_t opencfw_em9305_wsf_event_allocate(uint32_t);
extern uint32_t opencfw_em9305_wsf_task_message_send(uint32_t,uintptr_t);

/* Full native 0x325eb4..0x325eda.  R1 is captured into R13 during the
 * allocator BL delay slot; the event code write at +2 executes before send. */
uint32_t opencfw_em9305_init_transition_finish_325eb4(
    uintptr_t request,uint32_t reason)
{
    uintptr_t event=opencfw_em9305_wsf_event_allocate(4u);
    if(event==0u) return 0u;
    uint8_t identity=*(volatile uint8_t *)(request+1u);
    uint8_t handler=*(volatile uint8_t *)(uintptr_t)0x805b18u;
    *(volatile uint8_t *)(event+3u)=(uint8_t)reason;
    *(volatile uint16_t *)event=identity;
    *(volatile uint8_t *)(event+2u)=19u;
    return opencfw_em9305_wsf_task_message_send(handler,event);
}
