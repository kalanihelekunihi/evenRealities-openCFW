/* SPDX-License-Identifier: MIT */
/* GPIO clock enable precedes the observed control-register clear. */
#include <stdint.h>
extern void open_cfw_gx8002_platform_gate(unsigned int module, unsigned int enable);
int open_cfw_gx8002_gpio_initialize(void)
{
    open_cfw_gx8002_platform_gate(4, 1);
    *(volatile uint32_t *)(uintptr_t)0xa0001034 = 0;
    return 0;
}
