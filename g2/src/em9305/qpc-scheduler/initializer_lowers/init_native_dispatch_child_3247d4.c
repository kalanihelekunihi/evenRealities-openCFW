#include <stdint.h>
#include "em9305_ram.h"

/* Native 0x3247d4..0x3247f6: when the nested state byte (+64) is 1, move it
 * to 2 and post event 0x2000 to the WSF handler at ((uintptr_t)&em9305_ram_805af0 + 0x28u). Otherwise the
 * state byte is returned unchanged. */
extern uint32_t opencfw_em9305_wsf_event_post(uint32_t,uint32_t);

uint32_t opencfw_em9305_dispatch_child_3247d4(uintptr_t record)
{
    uintptr_t nested = *(volatile uint32_t *)(record + 0xafcu);
    uint32_t state = *(volatile uint8_t *)(nested + 64u);
    if (state != 1u) return state;
    uint32_t handler = em9305_ram_805af0.u8_805b18;
    *(volatile uint8_t *)(nested + 64u) = 2u;
    return opencfw_em9305_wsf_event_post(handler, 0x2000u);
}
