/* FlashDB's reflected IEEE CRC-32, source-derived from fdb_utils.c. */
#include <stddef.h>
#include <stdint.h>

uint32_t g2_flashdb_crc32(uint32_t crc, const void *buffer, size_t size)
{
    const uint8_t *p = (const uint8_t *)buffer;
    crc = ~crc;
    for (size_t i = 0; i < size; ++i) {
        crc ^= p[i];
        for (unsigned bit = 0; bit < 8; ++bit)
            crc = (crc >> 1) ^ ((crc & 1u) ? UINT32_C(0xedb88320) : 0u);
    }
    return ~crc;
}
