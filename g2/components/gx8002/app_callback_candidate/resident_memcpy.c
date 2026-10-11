/* SPDX-License-Identifier: MIT
 * Image-A SRAM 0x10025738..0x100257b5, native forward-copy helper.
 * The aligned path uses 16-, 4-, then 1-byte units; unaligned addresses
 * use bytes throughout. This is not a memmove contract.
 */
#include <stdint.h>

void gx8002_resident_memcpy_25738(
    void *destination, const void *source, uint32_t bytes)
{
    uintptr_t dst = (uintptr_t)destination;
    uintptr_t src = (uintptr_t)source;
    if (((dst | src) & 3u) == 0u) {
        while ((int32_t)bytes >= 16) {
            const volatile uint32_t *s = (const volatile uint32_t *)src;
            volatile uint32_t *d = (volatile uint32_t *)dst;
            uint32_t first = s[0];
            uint32_t second = s[1];
            uint32_t third = s[2];
            d[0] = first;
            uint32_t fourth = s[3];
            d[1] = second;
            d[2] = third;
            d[3] = fourth;
            src += 16u;
            dst += 16u;
            bytes -= 16u;
        }
        while ((int32_t)bytes >= 4) {
            *(volatile uint32_t *)dst = *(const volatile uint32_t *)src;
            src += 4u;
            dst += 4u;
            bytes -= 4u;
        }
    }
    while (bytes != 0u) {
        *(volatile uint8_t *)dst = *(const volatile uint8_t *)src;
        ++src;
        ++dst;
        --bytes;
    }
}
