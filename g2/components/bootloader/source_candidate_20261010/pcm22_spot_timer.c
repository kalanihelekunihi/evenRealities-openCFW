/* Source-owned PCM2.2 spot-timer start/stop leaves from locked instructions. */
#include <stdint.h>

#define WORD(address) (*(volatile uint32_t *)(uintptr_t)(address))

extern uint32_t clock_request(uint32_t clock_id, uint32_t user_id);
extern uint32_t clock_release(uint32_t clock_id, uint32_t user_id);

void opencfw_pcm22_spot_timer_start(uint32_t wait)
{
    (void)clock_request(4u, 0x31u);
    WORD(0x400083e8u) = wait * 6u;
    WORD(0x40008010u) |= 0x8000u;
    WORD(0x400083e0u) |= 2u;
    WORD(0x400083e0u) &= ~2u;
    WORD(0xe000e108u) = 0x40000u;
    WORD(0x400083e0u) |= 1u;
}

void opencfw_pcm22_spot_timer_stop(void)
{
    WORD(0x400083e0u) &= ~1u;
    WORD(0x40008010u) &= ~0x8000u;
    (void)clock_release(4u, 0x31u);
    WORD(0xe000e188u) = 0x40000u;
    WORD(0x40008068u) = 0xc0000000u;
    (void)WORD(0x47ff0000u);
    WORD(0xe000e288u) = 0x40000u;
}
