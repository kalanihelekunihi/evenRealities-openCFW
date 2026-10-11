/* SPDX-License-Identifier: MIT
 * Native XIP 0x10207644..0x1020765f: disable mask 0x20007 then
 * enable mask 0x10000 through selected interrupt-register provider.
 */
#include <stdint.h>

extern uint32_t gx8002_xip_audio_set_interrupt_enable_102047b8(
    uint32_t, uint32_t);

void gx8002_xip_audio_suspend_10207644(void)
{
    (void)gx8002_xip_audio_set_interrupt_enable_102047b8(0x20007u, 0u);
    (void)gx8002_xip_audio_set_interrupt_enable_102047b8(0x10000u, 1u);
}
