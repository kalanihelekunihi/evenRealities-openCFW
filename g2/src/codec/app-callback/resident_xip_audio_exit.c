/* SPDX-License-Identifier: MIT
 * Native XIP audio exit 0x10204984: reset AIN and disable gates 3,2,8,7.
 */
#include <stdint.h>

extern uint32_t gx8002_xip_ain_reset_10203c88(void);
extern void gx8002_resident_platform_gate_25080(uint32_t, uint32_t);

uint32_t gx8002_xip_audio_exit_10204984(void)
{
    (void)gx8002_xip_ain_reset_10203c88();
    gx8002_resident_platform_gate_25080(3u, 0u);
    gx8002_resident_platform_gate_25080(2u, 0u);
    gx8002_resident_platform_gate_25080(8u, 0u);
    gx8002_resident_platform_gate_25080(7u, 0u);
    return 0u;
}
