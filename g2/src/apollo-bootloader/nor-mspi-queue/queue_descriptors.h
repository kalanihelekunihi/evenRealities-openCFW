/* SPDX-License-Identifier: MIT */
#ifndef OPENCFW_BOOTLOADER_QUEUE_DESCRIPTORS_H
#define OPENCFW_BOOTLOADER_QUEUE_DESCRIPTORS_H

#include <stdint.h>

/* Stock Apollo private queue helpers recovered from 0x42790a/0x4279f0/
 * 0x427baa.  Pointers are 32-bit target addresses. */
uint32_t opencfw_provider_42790a(uint32_t *queue, uint32_t block_count,
                                uint32_t *block_address_out,
                                uint32_t *sequence_out);
uint32_t opencfw_provider_4279f0(uint32_t *queue, uint32_t command_kind);
uint32_t opencfw_provider_427baa(uint32_t *queue);

#endif
