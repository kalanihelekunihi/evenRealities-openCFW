/* SPDX-License-Identifier: MIT
 * CASE clock/UART prescaler tables. The 12-entry UART table is the retained
 * STM32G0 HAL UARTPrescTable definition. The 8-entry APB shift table is the
 * retained ST APBPrescTable definition with native CASE word-sized entries.
 * Both typed values match official CASE 2.2.6.10 at d380 and d3e8.
 */
#include <stdint.h>
const uint16_t case_boot_sensor_prescale_table[12]={
    1u,2u,4u,6u,8u,10u,12u,16u,32u,64u,128u,256u
};
const uint32_t case_boot_clock_shift_table[8]={0u,0u,0u,0u,1u,2u,3u,4u};
/* RCC AHBPrescTable from retained ST system source; CASE 0x0800d3a8. */
const uint32_t case_boot_ahb_shift_table[16]={
    0u,0u,0u,0u,0u,0u,0u,0u,1u,2u,3u,4u,6u,7u,8u,9u
};
