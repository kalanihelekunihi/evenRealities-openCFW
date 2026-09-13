/* SPDX-License-Identifier: MIT */
#include <stdint.h>
typedef struct { uint32_t gain:6, reserved:26; } gain_register;
typedef struct { uint32_t reserved:31, enable:1; } gain_control_register;

/* Recovered gain encoding: quotient bands 4..8 add 5,10,15,20,25.
 * Express the arithmetic progression directly, without a stock table. */
int open_cfw_gx8002_audio_pga_gain(uint32_t gain)
{
    uint32_t quotient=gain/6u;
    uint32_t correction=(quotient-4u<5u)?5u*(quotient-3u):0u;
    volatile gain_register *value=(volatile gain_register *)(uintptr_t)0xa0a001a4u;
    volatile gain_control_register *control=(volatile gain_control_register *)(uintptr_t)0xa0a001a0u;
    value->gain=gain%6u+quotient+correction;
    control->enable=1;
    return 0;
}
