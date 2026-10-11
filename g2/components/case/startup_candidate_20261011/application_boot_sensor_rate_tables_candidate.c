/* SPDX-License-Identifier: MIT
 * Native CASE 0x0800d398/0x0800d3a0 clock selection lookup values.
 * Control-bit selectors in 0x08004f14 index these exact eight entries.
 */
#include <stdint.h>
const uint8_t case_boot_sensor_divisor_table[8]={1u,1u,1u,3u,7u,1u,0u,0u};
const uint8_t case_boot_sensor_rate_table[8]={8u,4u,2u,4u,8u,1u,1u,1u};
_Static_assert(sizeof(case_boot_sensor_divisor_table)==8u,"divisor table extent");
_Static_assert(sizeof(case_boot_sensor_rate_table)==8u,"rate table extent");
