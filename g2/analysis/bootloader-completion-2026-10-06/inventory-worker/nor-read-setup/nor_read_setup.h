/* SPDX-License-Identifier: MIT */
#ifndef OPENCFW_BL_NOR_READ_SETUP_H
#define OPENCFW_BL_NOR_READ_SETUP_H

#include <stdint.h>

void opencfw_bl_nor_read_before(void);
void opencfw_bl_nor_read_configure(void);
void opencfw_bl_nor_read_delay(void);
void opencfw_bl_nor_read_after(void);
uint32_t opencfw_bl_mspi_ready_wait(uint32_t retries);

#endif
