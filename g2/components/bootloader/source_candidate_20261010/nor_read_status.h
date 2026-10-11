/* SPDX-License-Identifier: MIT */
#ifndef OPENCFW_BL_NOR_READ_STATUS_H
#define OPENCFW_BL_NOR_READ_STATUS_H

#include <stdint.h>

uint32_t opencfw_bl_mspi_status_transfer(uint32_t instruction,
    uint32_t address, uint32_t send_address, void *destination,
    uint32_t length);

#endif
