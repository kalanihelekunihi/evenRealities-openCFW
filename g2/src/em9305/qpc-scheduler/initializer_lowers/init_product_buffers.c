#include "init_lower_native.h"
#include "em9305_ram.h"

extern void *opencfw_em9305_memset(void *destination, uint32_t value, uint32_t bytes);

/* Native 0x317498..0x3174d6. Product bytes 58 and 57 independently size
 * two zeroed regions; each product pointer is reloaded after the first call.
 * Caller 0x3077f4 discards the second memset return. */
uint32_t opencfw_em9305_init_child_317498(void)
{
    uintptr_t product = (uintptr_t)init_read32(((uintptr_t)&em9305_ram_805c5c + 0x50u));
    uintptr_t buffer = (uintptr_t)init_read32(((uintptr_t)&em9305_ram_805be0 + 0x60u));
    uint32_t bytes = (uint32_t)init_read8(product + 58u) << 8;
    (void)opencfw_em9305_memset((void *)buffer, 0u, bytes);

    product = (uintptr_t)init_read32(((uintptr_t)&em9305_ram_805c5c + 0x50u));
    buffer = (uintptr_t)init_read32(((uintptr_t)&em9305_ram_805be0 + 0x5cu));
    bytes = (uint32_t)init_read8(product + 57u) << 9;
    return (uint32_t)(uintptr_t)opencfw_em9305_memset((void *)buffer, 0u, bytes);
}
