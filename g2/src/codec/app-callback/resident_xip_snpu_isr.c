/* SPDX-License-Identifier: MIT
 * Native image-A XIP 0x10205ce0 SNPU interrupt trampoline.
 * The state base 0x20027350 is independently established by selected
 * SNPU initialization/resume sources and their native SRAM literal.
 */
#include <stdint.h>

extern int32_t gx8002_xip_snpu_process_status_10205bd8(void);

void gx8002_xip_snpu_isr_10205ce0(void)
{
    volatile uint32_t *const state =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0x20027350);
    if (state[0] != 2u)
        (void)gx8002_xip_snpu_process_status_10205bd8();
}
