/* SPDX-License-Identifier: MIT
 * Native image-A XIP 0x102098a8 crc32 calls 0x102097f4 crc32_no_comp
 * with a complemented seed/result. Both algorithms are source-owned by
 * pinned NationalChip base/src/crc32.c, already selected in this image.
 * This adapter retains the three-register public call ABI omitted by the
 * decompiler's one-argument signature; the native callers pass R0/R1/R2.
 */
#include <stdint.h>

extern uint32_t crc32(uint32_t seed, const unsigned char *bytes,
                      unsigned int length);

uint32_t gx8002_xip_crc32_102098a8(
    uint32_t seed, const void *bytes, uint32_t length)
{
    return crc32(seed, bytes, length);
}
