/* SPDX-License-Identifier: MIT
 * Native CASE 0x08003b90 sensor receive binding restart.
 */
#include <stdint.h>
extern uint32_t case_boot_sensor_bind(uint32_t,uint32_t,uint32_t); /* 0x64ec */
uint32_t case_boot_transport_rx_restart(void)
{
    return case_boot_sensor_bind(0x20000e24u,0x20000108u,1u)==0u?1u:0u;
}
