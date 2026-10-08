/* SPDX-License-Identifier: MIT
 * Source reconstruction of stock wait selector gate 0x421548.
 */
#include "device_mode_wait.h"

extern uint32_t opencfw_boot_device_wait_service(uint32_t mode,
                                                uint32_t event,
                                                uint32_t flags,
                                                volatile uint32_t *result);

uint32_t opencfw_boot_device_mode_wait(uint32_t mode, uint32_t event,
                                      uint32_t flags,
                                      volatile uint32_t *result)
{
    const uint8_t selector = (uint8_t)mode;
    if (selector == 1u || selector == 3u || selector == 5u)
        return opencfw_boot_device_wait_service(selector, event, flags,
                                                result);
    return 6u;
}
