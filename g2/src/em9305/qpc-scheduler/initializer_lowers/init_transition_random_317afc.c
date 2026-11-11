#include <stdint.h>

extern uint32_t opencfw_em9305_pal_random_step(void);

/* Native 0x317afc..0x317b0e. Pinned GCC ARC machine descriptions at
 * third-party/manuals/gcc-arc-loop/arc.md:783-816 encode XBFU as
 * (((width-1)&31)<<5)|(position&31); descriptor4 means width1,position4.
 * The BMSK source at lines965-975 uses width-1, so operand3 keeps low4.
 * Stock BMSK 3 / XBFU 4 / ADD: low nibble plus bit 4. */
uint32_t opencfw_em9305_init_transition_random_317afc(void)
{
    uint32_t random=opencfw_em9305_pal_random_step();
    return (random&15u)+((random>>4u)&1u);
}
