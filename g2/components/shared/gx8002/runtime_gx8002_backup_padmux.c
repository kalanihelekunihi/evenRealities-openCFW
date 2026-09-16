/* SPDX-License-Identifier: MIT */
/* Backup check/set inline the register access instead of calling the primary
 * image's separate getter. Invalid function values still reach the write. */
#include <stdint.h>
static inline unsigned observed(unsigned pin)
{
    if (pin>32) return 255;
    volatile uint32_t *reg=(volatile uint32_t *)(uintptr_t)(0xa0010090u+4*(pin/8));
    return (*reg>>(4*(pin%8)))&15;
}
int open_cfw_gx8002_padmux_check(int pin,int function)
{
    if (pin<0 || function<0) return -1;
    return observed((unsigned)pin)==(unsigned)function ? 0 : -1;
}
int open_cfw_gx8002_padmux_set(int pin,int function)
{
    unsigned index=(unsigned)pin;
    if (index>32) return -1;
    unsigned shift=4*(index%8);
    volatile uint32_t *reg=(volatile uint32_t *)(uintptr_t)(0xa0010090u+4*(index/8));
    *reg=(*reg&~(15u<<shift))|(((unsigned)function&15u)<<shift);
    if (function<0) return -1;
    return ((*reg>>shift)&15u)==(unsigned)function ? 0 : -1;
}
