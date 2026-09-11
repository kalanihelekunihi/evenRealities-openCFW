/* SPDX-License-Identifier: MIT */
#include <stdint.h>

void *open_cfw_gx8002_channel_lookup(uint32_t channel)
{
    if (channel == 0) return (void *)(uintptr_t)0x2002e050;
    if (channel == 1) return (void *)(uintptr_t)0x2002e1cc;
    return (void *)0;
}
