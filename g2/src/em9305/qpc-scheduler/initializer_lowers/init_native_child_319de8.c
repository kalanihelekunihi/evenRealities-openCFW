#include <stdint.h>

/* Native 0x319de8..0x319e06: stop the record's timer at +808, clear the
 * timer-armed byte at +826 and set the pending byte at +2262. */
extern uint32_t opencfw_em9305_wsf_timer_stop(uintptr_t timer);

uint32_t opencfw_em9305_child_319de8(uintptr_t record)
{
    uint32_t status=opencfw_em9305_wsf_timer_stop(record+808u);
    *(volatile uint8_t *)(record+826u)=0u;
    *(volatile uint8_t *)(record+2262u)=1u;
    return status;
}
