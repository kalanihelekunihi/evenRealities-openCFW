/* SPDX-License-Identifier: GPL-3.0-or-later */

#include "runtime_crc32.h"

#define OPEN_CFW_BOOTLOADER_CRC32_POLYNOMIAL UINT32_C(0xEDB88320)

__attribute__((used, noinline))
uint32_t open_cfw_bootloader_crc32(
    uint32_t crc,
    const uint8_t *data,
    uint32_t size
)
{
    uint32_t index;

    for (index = 0U; index < size; ++index) {
        uint32_t bit;
        crc ^= data[index];
        for (bit = 0U; bit < 8U; ++bit) {
            uint32_t mask = UINT32_C(0) - (crc & UINT32_C(1));
            crc = (crc >> 1U) ^ (OPEN_CFW_BOOTLOADER_CRC32_POLYNOMIAL & mask);
        }
    }
    return crc;
}
