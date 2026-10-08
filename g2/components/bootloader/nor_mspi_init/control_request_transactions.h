/* SPDX-License-Identifier: MIT */
#ifndef OPENCFW_BOOTLOADER_CONTROL_REQUEST_TRANSACTIONS_H
#define OPENCFW_BOOTLOADER_CONTROL_REQUEST_TRANSACTIONS_H

#include <stdint.h>

uint32_t opencfw_hal_mspi_control_transaction_request(uint32_t handle,
                                                       uint32_t request,
                                                       void *config);
void opencfw_bl_control_request_completion(uint32_t handle);

#endif
