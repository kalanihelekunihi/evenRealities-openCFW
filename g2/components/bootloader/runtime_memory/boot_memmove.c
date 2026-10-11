/* SPDX-License-Identifier: MIT
 * Source-owned equivalent of the Boot runtime overlap copy at 0x4276bc.
 * The target uses faster aligned transfers; direction and byte effects are
 * the observable contract. Compile freestanding to avoid a library import.
 */
#include <stddef.h>
#include <stdint.h>

void opencfw_boot_memmove(void *destination, const void *source, size_t size)
{
    uint8_t *const dst = (uint8_t *)destination;
    const uint8_t *const src = (const uint8_t *)source;
    if (dst > src && (uintptr_t)dst - (uintptr_t)src < size) {
        for (size_t i = size; i != 0u; --i)
            dst[i - 1u] = src[i - 1u];
    } else {
        for (size_t i = 0u; i < size; ++i)
            dst[i] = src[i];
    }
}
