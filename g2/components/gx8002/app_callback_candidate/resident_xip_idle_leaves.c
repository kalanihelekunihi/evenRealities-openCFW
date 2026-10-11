/* SPDX-License-Identifier: MIT
 * Exact native XIP 0x1020861c is `jmp r15`; 0x10208620 is
 * `movi r0,0; jmp r15`. These are authenticated no-effect contracts.
 */
#include <stdint.h>

void gx8002_xip_idle_tick_1020861c(void)
{
}

uint32_t gx8002_xip_idle_buffer_initialize_10208620(void)
{
    return 0u;
}
