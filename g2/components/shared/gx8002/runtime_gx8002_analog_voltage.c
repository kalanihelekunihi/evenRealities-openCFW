/* SPDX-License-Identifier: MIT */
/* Recovered analog LDO voltage leaf at codec package 0x16704.
 * Preserve the full stock input domain: voltage can also set upper-nibble
 * bits; the merged value is narrowed to a byte before the word write.
 */
#include <stdint.h>
int open_cfw_gx8002_analog_voltage(uint32_t voltage)
{
    if (voltage == UINT32_MAX)
        return -1;
    volatile uint32_t *control = (volatile uint32_t *)0xa0005054u;
    *control = (voltage | (*control & 0xf0u)) & 0xffu;
    return 0;
}
