#include <stdint.h>

/* Native 0x327dbc..0x327dc6: MOV immediate, delayed jump through BLINK,
 * and a word store in the jump delay slot. R0 is the address on return. */
uintptr_t opencfw_em9305_init_transition_refresh_327dbc(void)
{
    const uintptr_t address=(uintptr_t)0x805398u;
    *(volatile uint32_t *)address=0u;
    return address;
}
