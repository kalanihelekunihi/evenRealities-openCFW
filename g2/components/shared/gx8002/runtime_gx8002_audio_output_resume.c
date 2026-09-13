/* SPDX-License-Identifier: MIT */
#include <stdint.h>
extern void open_cfw_gx8002_platform_gate(uint32_t,uint32_t);
int open_cfw_gx8002_aout_resume(void *handle)
{
    open_cfw_gx8002_platform_gate(11,1);
    open_cfw_gx8002_platform_gate(15,1);
    volatile uint8_t *state=(volatile uint8_t *)handle;
    if (state[27]) {
        volatile uint32_t *irq=(volatile uint32_t *)0xa0b00008u;
        *irq=*irq|1u;
    }
    if (state[26]) state[26]=0;
    return 0;
}
