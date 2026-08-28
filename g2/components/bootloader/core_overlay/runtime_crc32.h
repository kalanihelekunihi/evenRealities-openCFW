/* SPDX-License-Identifier: MIT */

#ifndef OPEN_CFW_BOOTLOADER_RUNTIME_CRC32_H
#define OPEN_CFW_BOOTLOADER_RUNTIME_CRC32_H

#include <stdint.h>

uint32_t open_cfw_bootloader_crc32(
    uint32_t crc,
    const uint8_t *data,
    uint32_t size
);

#endif
