/* SPDX-License-Identifier: MIT */
#ifndef OPENCFW_BOOT_NOR_REGISTER_ID_H
#define OPENCFW_BOOT_NOR_REGISTER_ID_H

#include <stdint.h>

uint32_t opencfw_read_mspi_register_id(uint32_t register_id,
                                      uint32_t *out_value);

#endif
