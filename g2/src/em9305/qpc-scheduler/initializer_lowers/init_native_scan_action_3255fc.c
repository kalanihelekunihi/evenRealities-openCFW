#include <stdint.h>

/* Native 0x3255fc..0x325616: when the scan-active byte is set, mark the
 * pending byte at 0x805070 and notify the scheduler with 0x80506d. */
extern uint32_t opencfw_em9305_ll_schedule_notify_313354(uintptr_t object);

uint32_t opencfw_em9305_scan_action_3255fc(void)
{
    uint32_t active=*(volatile uint8_t *)0x805a73u;
    if(active==0u)return 0u;
    *(volatile uint8_t *)0x80506du=1u;
    return opencfw_em9305_ll_schedule_notify_313354(0x805070u);
}
