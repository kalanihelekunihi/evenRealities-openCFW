/* SPDX-License-Identifier: MIT
 * Link-only test services for power-domain branches excluded from selector
 * coverage (20, 23, and 29). The chain verifier asserts these are not called.
 */
#include <stdint.h>
#include <stddef.h>

uint32_t opencfw_boot_control_delay_status_change(
    uint32_t timeout, volatile uint32_t *address, uint32_t mask,
    uint32_t expected)
{
    (void)timeout; (void)address; (void)mask; (void)expected;
    return 0u;
}

uint32_t opencfw_boot_power_special_mode(uint32_t mode)
{
    (void)mode;
    return 0u;
}

uint32_t opencfw_bl_clock_release_all(uint32_t user)
{
    (void)user;
    return 0u;
}
