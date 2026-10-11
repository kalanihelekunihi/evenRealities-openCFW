/* SPDX-License-Identifier: MIT
 * Native XIP 0x10204340 and 0x1020452c. Both use direct AIN MMIO
 * rooted at 0xa0a00000; writes remain separate in native order.
 */
#include <stdint.h>

static volatile uint32_t *const ain =
    (volatile uint32_t *)(uintptr_t)UINT32_C(0xa0a00000);

uint32_t gx8002_xip_audio_set_i2sout_mode_10204340(uint32_t mode)
{
    ain[8u / 4u] = (ain[8u / 4u] & ~UINT32_C(0x10)) |
                   ((mode & 1u) << 4u);
    return 0u;
}

uint32_t gx8002_xip_audio_set_logfbank_enable_1020452c(
    uint32_t enable, uint32_t hmt)
{
    volatile uint32_t *reg = &ain[0x180u / 4u];
    *reg = (*reg & ~UINT32_C(0x10000000)) | ((hmt & 1u) << 28u);
    *reg = (*reg & ~UINT32_C(0x20000000)) | ((enable & 1u) << 29u);
    *reg = (*reg & ~UINT32_C(0x40000000)) | ((enable & 1u) << 30u);
    *reg = (*reg & ~UINT32_C(0x80000000)) |
           ((enable == 0u ? 1u : 0u) << 31u);
    return 0u;
}
