/* SPDX-License-Identifier: MIT */
#ifndef OPENCFW_BOOT_MODE_PUBLISHER_H
#define OPENCFW_BOOT_MODE_PUBLISHER_H

#include <stdint.h>

uint32_t opencfw_publish_mspi_mode(uint32_t module, uint32_t mode);
void opencfw_bl_mspi_mode_publish_core(uint32_t module, uint32_t mode);

#endif
