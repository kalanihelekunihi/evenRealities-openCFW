/* SPDX-License-Identifier: MIT */
#ifndef OPENCFW_BOOTLOADER_NOR_MSPI_QUEUE_H
#define OPENCFW_BOOTLOADER_NOR_MSPI_QUEUE_H

#include <stdint.h>

void opencfw_bl_mspi_clockgen_control(uint32_t module, uint32_t enable,
                                     uint32_t configure, uint32_t source);
void opencfw_hal_mspi_cq_init(uint32_t module, uint32_t queue_size_input,
                              uint32_t queue_buffer_address);
void opencfw_bl_mspi_cq_enable(uint32_t mspi_state_address);
uint32_t opencfw_hal_mspi_cq_disable(uint32_t mspi_state_address);
void opencfw_hal_mspi_cq_term(uint32_t mspi_state_address);

/* Source symbols corresponding to stock Apollo510 command-queue functions. */
uint32_t opencfw_provider_427794(uint32_t interface_id,
                                const void *config,
                                void **handle_slot);
uint32_t opencfw_provider_427878(uint32_t *queue_handle);
uint32_t opencfw_provider_4278c8(uint32_t *queue_handle);
uint32_t opencfw_provider_427ad6(uint32_t *queue_handle, uint32_t force);

#endif
