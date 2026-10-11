/* SPDX-License-Identifier: MIT
 * Image-A XIP 0x102099cc aligned memset body. Native decomp confirms the
 * byte-alignment prefix, four-word bulk path, and byte remainder.
 */
#include <stdint.h>

void gx8002_xip_memset_102099cc(void *destination, uint32_t value,
                                 uint32_t size)
{
    uint8_t *out = (uint8_t *)destination;
    uint8_t byte = (uint8_t)value;
    while (size != 0u && ((uintptr_t)out & 3u) != 0u) {
        *out++ = byte;
        --size;
    }
    uint32_t word = (uint32_t)byte * UINT32_C(0x01010101);
    uint32_t *wide = (uint32_t *)(void *)out;
    while (size >= 16u) {
        wide[0] = word;
        wide[1] = word;
        wide[2] = word;
        wide[3] = word;
        wide += 4;
        size -= 16u;
    }
    while (size >= 4u) {
        *wide++ = word;
        size -= 4u;
    }
    out = (uint8_t *)(void *)wide;
    while (size-- != 0u) *out++ = byte;
}
