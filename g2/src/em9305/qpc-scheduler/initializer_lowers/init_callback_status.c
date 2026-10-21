#include "init_lower_native.h"

/* Native 0x307a18..0x307a24 and 0x307b60..0x307b6c. Table contents are
 * product data at fixed stock addresses; no function body is inferred from
 * the table pointer. ARC ld.as indexes a word table with index*4. */
uint32_t opencfw_em9305_callback_307a18(uint32_t index)
{
    uint32_t context = init_read32(0x3357a8u + (uintptr_t)index * 4u);
    return init_read8((uintptr_t)context) != 0u;
}

uint32_t opencfw_em9305_callback_307b60(uint32_t index)
{
    uint32_t context = init_read32(0x3357b4u + (uintptr_t)index * 4u);
    return init_read8((uintptr_t)context) != 0u;
}
