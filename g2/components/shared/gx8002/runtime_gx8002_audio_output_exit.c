/* SPDX-License-Identifier: MIT */
#include <stdint.h>
extern void open_cfw_gx8002_platform_gate(uint32_t module, uint32_t enable);
/* Package e8d0: separate word updates precede ordered gate calls. */
int open_cfw_gx8002_aout_exit(void)
{
    volatile uint32_t *control=(volatile uint32_t *)0xa0b00020u;
    for (uint32_t mask=2;mask<=8;mask<<=1)
        *control=*control&~mask;
    open_cfw_gx8002_platform_gate(11,0);
    open_cfw_gx8002_platform_gate(15,0);
    return 0;
}
