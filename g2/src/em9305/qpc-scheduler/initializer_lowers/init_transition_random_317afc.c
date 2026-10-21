#include <stdint.h>

extern uint32_t opencfw_em9305_pal_random_step(void);

/* Native 0x317afc..0x317b0e. Pinned GCC ARC machine descriptions at
 * third-party/manuals/gcc-arc-loop/arc.md:783-816 encode XBFU as
 * (((width-1)&31)<<5)|(position&31); descriptor4 means width1,position4.
 * The BMSK source at lines965-975 uses width-1, so operand3 keeps low4.
 * Keep the exact named pair on target; host uses the source-derived value. */
uint32_t opencfw_em9305_init_transition_random_317afc(void)
{
    uint32_t random=opencfw_em9305_pal_random_step();
#ifdef __arc__
    uint32_t low,high;
    __asm__ volatile("bmsk %0,%2,0x3\n\txbfu %1,%2,0x4\n\tadd %1,%1,%0"
        :"=&r"(low),"=&r"(high):"r"(random):"cc");
    return high;
#else
    return (random&15u)+((random>>4u)&1u);
#endif
}
