/* SPDX-License-Identifier: MIT. Reconstructed source for stock query helpers. */
#ifndef OPENCFW_BOOT_PLATFORM_CONTROL_RUNTIME_QUERY_H
#define OPENCFW_BOOT_PLATFORM_CONTROL_RUNTIME_QUERY_H

#include <stdint.h>

uint32_t opencfw_boot_control_query_descriptor_copy(uint32_t *destination,
                                                     uint32_t selector);
uint32_t opencfw_boot_control_query(uint32_t selector, uint8_t *result);

#endif
