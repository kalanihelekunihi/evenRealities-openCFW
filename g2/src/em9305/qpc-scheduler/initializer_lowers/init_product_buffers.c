#include "init_lower_native.h"

extern void *opencfw_em9305_memset(void *destination, uint32_t value, uint32_t bytes);

/* Native 0x317498..0x3174d6. Product bytes 58 and 57 independently size
 * two zeroed regions; each product pointer is reloaded after the first call.
 * Caller 0x3077f4 discards the second memset return. */
uint32_t opencfw_em9305_init_child_317498(void)
{
    uintptr_t product = (uintptr_t)init_read32(0x805cacu);
    uintptr_t buffer = (uintptr_t)init_read32(0x805c40u);
    uint32_t bytes = (uint32_t)init_read8(product + 58u) << 8;
    (void)opencfw_em9305_memset((void *)buffer, 0u, bytes);

    product = (uintptr_t)init_read32(0x805cacu);
    buffer = (uintptr_t)init_read32(0x805c3cu);
    bytes = (uint32_t)init_read8(product + 57u) << 9;
    return (uint32_t)(uintptr_t)opencfw_em9305_memset((void *)buffer, 0u, bytes);
}
