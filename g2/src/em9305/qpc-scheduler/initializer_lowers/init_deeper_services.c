#include "init_lower_native.h"

extern void *opencfw_em9305_memset(void *destination, uint32_t value, uint32_t bytes);

/* Native 0x3251dc..0x32520a: ordered registry membership, then append.
 * The stock code does not check table capacity; this source preserves that
 * caller/product capacity contract rather than inventing a guard. */
uint32_t opencfw_em9305_init_child_3251dc(uint32_t callback)
{
    uint32_t count = init_read8(0x8027ccu);
    for (uint32_t index = 0u; index < count; ++index)
        if (init_read32(0x8027d0u + 4u * index) == callback)
            return callback;
    *(volatile uint8_t *)0x8027ccu = (uint8_t)(count + 1u);
    init_write32(0x8027d0u + 4u * count, callback);
    return callback;
}

/* Native 0x318ab8..0x318ad2. Input R0 is overwritten by the product
 * pointer before any use; a low-word unsigned multiply sizes the clear. */
uint32_t opencfw_em9305_init_child_318ab8(uint32_t previous_result)
{
    (void)previous_result;
    uintptr_t product = (uintptr_t)init_read32(0x805cacu);
    uint32_t count = init_read8(product + 34u);
    uintptr_t destination = (uintptr_t)init_read32(0x805c70u);
    uint32_t bytes = count * 912u;
    return (uint32_t)(uintptr_t)opencfw_em9305_memset((void *)destination, 0u, bytes);
}
