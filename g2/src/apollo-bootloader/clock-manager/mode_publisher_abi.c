/* SPDX-License-Identifier: MIT
 * Stock MSPI mode publisher entry (also reached as the device-mode publisher).
 * Stock returns a stale register; callers ignore the result. */
#include <stdint.h>
#include "mode_publisher.h"

uint32_t opencfw_publish_mspi_mode(uint32_t module, uint32_t mode)
{
    opencfw_bl_mspi_mode_publish_core(module, mode);
    return 0u;
}

__typeof__(opencfw_publish_mspi_mode) opencfw_publish_device_mode
    __attribute__((alias("opencfw_publish_mspi_mode")));
