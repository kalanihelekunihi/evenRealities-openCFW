/* SPDX-License-Identifier: MIT
 * Locked descriptor callback interfaces for application storage at 0x200001e8.
 */
#ifndef OPENCFW_BOOT_STORAGE_CALLBACKS_H
#define OPENCFW_BOOT_STORAGE_CALLBACKS_H

#include <stdint.h>

uint32_t opencfw_boot_storage_range_valid(uint32_t address, uint32_t size);
uint32_t opencfw_boot_storage_read(void *destination, const void *source,
                                   uint32_t size);
uint32_t opencfw_boot_storage_program(uint32_t destination,
                                      const void *source, uint32_t size);
uint32_t opencfw_boot_storage_erase_validate(uint32_t destination);

#endif
