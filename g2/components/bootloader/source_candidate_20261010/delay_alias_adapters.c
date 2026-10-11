/* SPDX-License-Identifier: MIT
 * Historical source-image names for the reviewed stock delay wrappers.
 * The authored assembly preserves the original R7-to-R0 return convention.
 */
#include <stdint.h>

extern uint32_t opencfw_boot_delay_scaled(uint32_t value);
extern uint32_t opencfw_boot_delay_raw(uint32_t value);

uint32_t opencfw_bl_delay(uint32_t value)
{
    return opencfw_boot_delay_scaled(value);
}

uint32_t opencfw_bl_delay_raw(uint32_t value)
{
    return opencfw_boot_delay_raw(value);
}

uint32_t opencfw_provider_41f9d8(uint32_t value)
{
    return opencfw_boot_delay_scaled(value);
}
