/* SPDX-License-Identifier: MIT */
#ifndef OPENCFW_BOOTLOADER_CONTROL_REQUEST_EXTENSION_H
#define OPENCFW_BOOTLOADER_CONTROL_REQUEST_EXTENSION_H

#include <stdint.h>

/* Provider used by the 0x4251c0 control dispatcher for requests 31 and 33.
 * Request 33 depends on the recovered stock continuation at 0x4240aa. */
uint32_t opencfw_hal_mspi_control_queue_request(uint32_t handle,
                                                uint32_t request,
                                                void *config);

#endif
