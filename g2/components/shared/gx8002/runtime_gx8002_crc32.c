/* SPDX-License-Identifier: MIT */
/* Reflected CRC-32, with aligned word ingestion matching the stock algorithm.
 * Ordinary readable memory only. Table is generated from polynomial 0xEDB88320.
 */
#include <stdint.h>
extern const uint32_t open_cfw_gx8002_crc_table[256];
typedef uint32_t crc_word __attribute__((__may_alias__));

static inline uint32_t step(uint32_t value)
{
    return open_cfw_gx8002_crc_table[value & 255U] ^ (value >> 8);
}

uint32_t open_cfw_gx8002_crc32_no_comp(uint32_t crc, const unsigned char *data, unsigned int size)
{
    while (size && ((uintptr_t)data & 3U)) {
        crc = step(crc ^ *data++);
        --size;
    }
    while (size >= 4) {
        /* Explicit little-endian target. Host test is also little-endian. */
        crc ^= *(const crc_word *)data;
        crc = step(step(step(step(crc))));
        data += 4;
        size -= 4;
    }
    while (size) {
        crc = step(crc ^ *data++);
        --size;
    }
    return crc;
}

uint32_t open_cfw_gx8002_crc32(uint32_t initial, const unsigned char *data, unsigned int size)
{
    return open_cfw_gx8002_crc32_no_comp(initial ^ UINT32_MAX, data, size) ^ UINT32_MAX;
}
