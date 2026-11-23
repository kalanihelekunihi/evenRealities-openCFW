#include <stdint.h>
#include "em9305_ram.h"

/* Native 0x3255fc..0x325616: when the scan-active byte is set, mark the
 * pending byte at ((uintptr_t)&em9305_ram_80505c + 0x14u) and notify the scheduler with ((uintptr_t)&em9305_ram_80505c + 0x11u). */
extern uint32_t opencfw_em9305_ll_schedule_notify_313354(uintptr_t object);

uint32_t opencfw_em9305_scan_action_3255fc(void)
{
    uint32_t active=*(volatile uint8_t *)((uintptr_t)&em9305_ram_805a6c + 0x7u);
    if(active==0u)return 0u;
    *(volatile uint8_t *)((uintptr_t)&em9305_ram_80505c + 0x11u)=1u;
    return opencfw_em9305_ll_schedule_notify_313354(((uintptr_t)&em9305_ram_80505c + 0x14u));
}
