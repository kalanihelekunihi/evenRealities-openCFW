/* SPDX-License-Identifier: MIT
 * Size-only candidate. Polynomial and complement convention are derived from
 * pinned NationalChip crc32.c; slower timing has not been qualified.
 */
#include <stdint.h>

uint32_t gx8002_image_b_crc32_raw_1000c510(
    uint32_t crc, const unsigned char *buf, unsigned int len)
{
    while (len--) {
        crc ^= *buf++;
        for (unsigned int bit = 0; bit < 8; bit++)
            crc = (crc >> 1) ^ ((crc & 1u) ? UINT32_C(0xedb88320) : 0u);
    }
    return crc;
}

uint32_t gx8002_image_b_crc32_1000c5c4(
    uint32_t crc, const unsigned char *buf, unsigned int len)
{
    return gx8002_image_b_crc32_raw_1000c510(crc ^ UINT32_MAX, buf, len) ^ UINT32_MAX;
}
