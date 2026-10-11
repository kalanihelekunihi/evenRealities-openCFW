/* SPDX-License-Identifier: MIT
 * Policy call at native 0x598c shares the sourced bus frequency setter.
 */
#include <stdint.h>
extern uint32_t case_boot_bus_set_frequency(uint32_t descriptor,uint32_t frequency,uint32_t width);
void case_policy_flash_write(uint32_t descriptor,uint32_t frequency,uint32_t width)
{(void)case_boot_bus_set_frequency(descriptor,frequency,width);}
