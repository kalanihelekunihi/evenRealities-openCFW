/* SPDX-License-Identifier: MIT */
#ifndef OPENCFW_BL_NOR_READ_H
#define OPENCFW_BL_NOR_READ_H

#include <stdint.h>

uint32_t opencfw_boot_nor_read(uint32_t address, void *destination,
                               uint32_t length, uint32_t reserved);

#endif
