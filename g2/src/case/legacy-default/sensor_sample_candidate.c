/* SPDX-License-Identifier: MIT
 * Stock 0x0800a528 sampling through the 0x08004e94 masked register read
 * (called, as stock, so the sample point within the bit cell matches).
 * Sensor electrical levels at 0x50000410 remain runtime data.
 */
#include <stdint.h>
extern uint32_t case_init_pin_read(uint32_t base,uint32_t mask); /* 0x08004e94 */
/* Stock 0x0800A528 (case_select_mask) */
uint32_t case_binary_sensor_sample(void)
{
    uint32_t mask=*(volatile uint8_t *)(uintptr_t)0x20000114u ? 8u : 16u;
    return case_init_pin_read(0x50000400u,mask)!=0u;
}
