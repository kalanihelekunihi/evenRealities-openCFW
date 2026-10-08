/* SPDX-License-Identifier: MIT */
#ifndef OPENCFW_BOOTLOADER_CONTROL_REQUEST34_H
#define OPENCFW_BOOTLOADER_CONTROL_REQUEST34_H
#include <stdint.h>
uint32_t opencfw_hal_mspi_control_request34(uint32_t handle,void *config);
uint32_t opencfw_hal_mspi_control_request34_dispatch(uint32_t handle,
                                                      uint32_t request,
                                                      void *config);
void opencfw_bl_control_request34_noop(uint32_t unused);
#endif
