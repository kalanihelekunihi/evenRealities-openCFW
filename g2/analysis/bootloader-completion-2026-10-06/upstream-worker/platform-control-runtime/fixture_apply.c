/* SPDX-License-Identifier: MIT. Entry is intercepted by the offline fixture. */
#include <stdint.h>
uint32_t opencfw_boot_control_power_apply_configure(uint32_t *object,
                                                    uint32_t operation,
                                                    uint8_t enable)
{
    (void)object;
    (void)operation;
    (void)enable;
    return 0u;
}
void opencfw_boot_control_delay_us(uint32_t microseconds)
{ (void)microseconds; }
uint32_t opencfw_boot_control_delay_status_change(uint32_t timeout,
                                                   volatile uint32_t *address,
                                                   uint32_t mask,
                                                   uint32_t expected)
{ (void)timeout; (void)address; (void)mask; (void)expected; return 0u; }
