/* SPDX-License-Identifier: MIT
 * Native CASE 0x08006b80/0x08006b98 GPIO control leaves.
 */
#include <stdint.h>
extern void case_control_write(uint32_t base,uint32_t mask,uint32_t enable); /* 0x4e9e */
void case_boot_transport_stop_clock(uint32_t value)
{
    case_control_write(0x50000000u,0x40u,value!=0u);
}
void case_boot_transport_stop_link(uint32_t value)
{
    case_control_write(0x50000000u,0x80u,value!=0u);
}
