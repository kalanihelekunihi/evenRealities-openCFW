/* SPDX-License-Identifier: MIT
 * Stock 0x0800a528 sampling, inlining the simple 0x08004e94 masked
 * register read. Sensor electrical levels at 0x50000410 remain runtime data.
 */
#include <stdint.h>
uint32_t case_binary_sensor_sample(void)
{
    uint32_t mask=*(volatile uint8_t *)(uintptr_t)0x20000114u ? 8u : 16u;
    return (*(volatile uint32_t *)(uintptr_t)0x50000410u & mask)!=0u;
}
