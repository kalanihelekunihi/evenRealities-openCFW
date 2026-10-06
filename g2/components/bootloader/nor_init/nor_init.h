/* SPDX-License-Identifier: MIT */
#ifndef OPENCFW_BOOTLOADER_NOR_INIT_H
#define OPENCFW_BOOTLOADER_NOR_INIT_H

#include <stdint.h>

/* Provider for locked bootloader entry 0x00420476. */
uint32_t opencfw_provider_420476(void);

/* Small JEDEC-ID helper called by 0x00420476 (locked entry 0x0042059e). */
uint32_t opencfw_bl_nor_read_jedec_id(uint32_t *out_id,
                                      uint32_t reserved1,
                                      uint32_t reserved2,
                                      uint32_t initial_word);

#endif
