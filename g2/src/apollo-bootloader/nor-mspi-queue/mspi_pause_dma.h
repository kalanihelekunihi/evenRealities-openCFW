/* SPDX-License-Identifier: MIT */
#ifndef OPENCFW_BOOTLOADER_MSPI_PAUSE_DMA_H
#define OPENCFW_BOOTLOADER_MSPI_PAUSE_DMA_H

#include <stdint.h>

/* Reconstructed stock 0x4240aa state transition, including its 0x423fb8
 * pause/poll and 0x42403e DMA-configuration continuations. */
uint32_t opencfw_provider_4240aa(uint32_t *mspi_state,
                                uint32_t timeout_increment);

#endif
