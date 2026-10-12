/* SPDX-License-Identifier: MIT
 * Behavioral size variant for native 0x1000c510 raw CRC and 0x1000c5c4
 * complemented wrapper. The reflected polynomial and complement convention
 * are authenticated by the byte-identical native table and pinned NationalChip
 * tools/uart_adpcm/crc/crc32.c at commit
 * 8bf9ee5cb6eeb226011e61c15fa4981b83b93bd5. This computes the same
 * remainder without the 1024-byte table; execution timing is unqualified.
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
