#include <stdint.h>

/* Native 0x303f80..0x303f8a: guard interval, the halfword at +6 of the
 * timing configuration (*0x805c18). */
uint32_t opencfw_em9305_auxiliary_guard_interval(void)
{
    uintptr_t timing=*(volatile uint32_t *)(uintptr_t)0x805c18u;
    return *(volatile uint16_t *)(timing+6u);
}

static uint32_t mulhi_312c5c(uint32_t a,uint32_t b)
{
    return (uint32_t)(((uint64_t)a*b)>>32);
}

/* Native 0x312c5c..0x312c9e: round a duration (us) up to the sync-offset
 * unit: 30 us below 0x3bfc4 us, 300 us above. The stock divisions are
 * reciprocal multiplies and the 16-bit unit multiplies keep only the low
 * halfword of the quotient. */
uint32_t opencfw_em9305_channel_timing_adjust_312c5c(uint32_t duration)
{
    uint32_t rounded;
    if(duration<0x3bfc4u) {
        uint32_t units=mulhi_312c5c(duration,0x11111112u)>>1;
        rounded=(units&0xffffu)*30u;
        return rounded>=duration?rounded:rounded+30u;
    }
    uint32_t units=(duration*3u+mulhi_312c5c(duration,0x69d0369eu))>>10;
    rounded=300u*(units&0xffffu);
    return rounded>=duration?rounded:rounded+300u;
}
