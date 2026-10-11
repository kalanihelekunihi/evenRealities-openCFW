/* SPDX-License-Identifier: MIT
 * Native CASE 0x0800d250: snapshot eight sensor state bytes.
 */
#include <stdint.h>
void case_policy_sensor_prepare(void)
{
    volatile uint8_t *state=(volatile uint8_t *)(uintptr_t)0x20000090u;
    for(uint32_t i=0u;i<8u;++i)state[i+8u]=state[i];
}
