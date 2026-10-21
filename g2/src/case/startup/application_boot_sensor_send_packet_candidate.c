/* SPDX-License-Identifier: MIT
 * Native CASE 0x08003bb0 descriptor-bound packet transmit wrapper.
 */
#include <stdint.h>
extern uint32_t case_boot_sensor_transfer(uint32_t descriptor,const uint8_t *packet,
                                          uint32_t count,uint32_t timeout); /* 0x66ac */
uint32_t case_boot_sensor_send_packet(const uint8_t *packet,uint32_t count)
{
    return case_boot_sensor_transfer(0x20000eb8u,packet,count,0xffffu);
}
