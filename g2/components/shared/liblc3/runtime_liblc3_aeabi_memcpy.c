/*
 * Bounded local AEABI memcpy helper for size-optimized LC3 builds.
 *
 * Clang's Cortex-M size pipeline may lower a non-overlapping fixed-size copy
 * to __aeabi_memcpy even with -fno-builtin.  Keeping that compiler helper in
 * the LC3 closure prevents a size experiment from acquiring a twelfth target
 * runtime binding.  The volatile byte accesses also prevent this definition
 * from being recursively lowered to itself.
 *
 * SPDX-License-Identifier: MIT
 */

#include <stddef.h>
#include <stdint.h>

void __aeabi_memcpy(void *destination, const void *source, size_t count)
{
    volatile uint8_t *output = (volatile uint8_t *)destination;
    const volatile uint8_t *input = (const volatile uint8_t *)source;
    size_t index;

    for (index = 0U; index < count; ++index) {
        output[index] = input[index];
    }
}
