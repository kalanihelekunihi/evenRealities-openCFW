/* SPDX-License-Identifier: MIT
 * Image-A XIP 0x10206c44 overlap-aware memmove. Forward path calls the
 * existing source-owned SRAM memcpy at 0x10025738; reverse path copies
 * bytes from the end as retained native pseudocode shows.
 */
#include <stdint.h>

extern void gx8002_resident_memcpy_25738(
    void *destination, const void *source, uint32_t bytes);

void *gx8002_xip_tws_shift_10206c44(
    void *destination, const void *source, uint32_t bytes)
{
    uint8_t *dst = (uint8_t *)destination;
    const uint8_t *src = (const uint8_t *)source;
    if ((uintptr_t)dst < (uintptr_t)src)
        gx8002_resident_memcpy_25738(dst, src, bytes);
    else
        while (bytes != 0u) {
            --bytes;
            dst[bytes] = src[bytes];
        }
    return destination;
}
