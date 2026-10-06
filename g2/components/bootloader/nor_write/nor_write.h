/* SPDX-License-Identifier: MIT */
#ifndef OPENCFW_BOOTLOADER_NOR_WRITE_H
#define OPENCFW_BOOTLOADER_NOR_WRITE_H
#include <stdint.h>

uint32_t opencfw_provider_420b0c(uint32_t address, const void *source,
                                uint32_t length);
uint32_t opencfw_provider_420a08(uint32_t address);
uint32_t opencfw_provider_420984(void); /* MX25 WREN (0x06) */
uint32_t opencfw_provider_4209c4(void); /* MX25 WRDI (0x04) */

#endif
