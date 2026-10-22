/* SPDX-License-Identifier: MIT
 * Native CASE 0x08005f00 sensor descriptor shutdown.
 */
#include <stdint.h>
extern void case_policy_sensor_stop(uint32_t descriptor); /* 0x62ac */

/* Stock 0x08005F00 (case_reset_controller_context) */
uint32_t case_policy_sensor_shutdown(uint32_t descriptor)
{
    if(descriptor==0u)return 1u;
    volatile uint32_t *desc=(volatile uint32_t *)(uintptr_t)descriptor;
    volatile uint32_t *status=(volatile uint32_t *)(uintptr_t)(descriptor+0x80u);
    status[2u]=36u;
    volatile uint32_t *device=(volatile uint32_t *)(uintptr_t)desc[0u];
    device[0u]&=~1u;
    device[0u]=0u;
    device[1u]=0u;
    device[2u]=0u;
    case_policy_sensor_stop(descriptor);
    status[4u]=0u;
    status[2u]=0u;
    status[3u]=0u;
    desc[27u]=0u;
    desc[28u]=0u;
    *(volatile uint8_t *)(uintptr_t)(descriptor+0x84u)=0u;
    return 0u;
}
