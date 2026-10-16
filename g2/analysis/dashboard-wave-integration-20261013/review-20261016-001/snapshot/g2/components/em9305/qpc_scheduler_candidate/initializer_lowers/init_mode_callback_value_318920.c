#include <stdint.h>

/* Complete native 0x318920..0x31895e. The 0x303f5c child reads a live
 * configuration halfword through 0x805c18. All native BRLO delay-slot
 * assignments are represented in their actual threshold order. */
uint32_t opencfw_em9305_mode_callback_value_318920(uintptr_t context)
{
    uintptr_t configuration=*(volatile uint32_t *)(uintptr_t)0x805c18u;
    uint32_t value=*(volatile uint16_t *)configuration;
    uint32_t rank;
    if (value<21u) rank=7u;
    else if (value<31u) rank=6u;
    else if (value<51u) rank=5u;
    else if (value<76u) rank=4u;
    else if (value<101u) rank=3u;
    else if (value<151u) rank=2u;
    else rank=(value<251u)?1u:0u;
    uint32_t local=*(volatile uint8_t *)(context+746u);
    return (uint8_t)(rank+local);
}
