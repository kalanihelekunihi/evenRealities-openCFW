/* SPDX-License-Identifier: MIT */
#ifndef OPENCFW_NOR_RUNTIME_HELPERS_H
#define OPENCFW_NOR_RUNTIME_HELPERS_H
#include <stdint.h>
void opencfw_provider_41fe9c(void);
void opencfw_provider_41fed4(void);
void opencfw_bl_nor_read_before(void);
void opencfw_bl_nor_read_after(void);
void opencfw_bl_nor_read_configure(void);
uint32_t opencfw_bl_nor_busy(void);
uint32_t opencfw_bl_nor_wait(uint32_t count);
uint32_t opencfw_bl_nor_read_delay(void);
void opencfw_hal_mspi_control_latency(uint32_t enabled);
#endif
