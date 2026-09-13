/* SPDX-License-Identifier: MIT */
/* Recovered gx_analog_get_ldo_dig_ctrl at codec package 0x16724.
 * One volatile word read; bit 2 selects software control, bit 1 bypass.
 */
#include <stdint.h>
unsigned open_cfw_gx8002_digital_control(void)
{
    uint32_t value = *(volatile uint32_t *)0xa0005058u;
    return (value & 4u) ? 1u + ((value >> 1) & 1u) : 0u;
}
