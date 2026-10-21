/* SPDX-License-Identifier: MIT. Main 0x4d3938 class 4 trigger register. */
#include <stdint.h>

uint32_t g2_main_clock_class4_trigger_4d3938(uint32_t value)
{
    *(volatile uint32_t *)(uintptr_t)UINT32_C(0x40004020) = value | 1u;
    return 0u;
}
