/* SPDX-License-Identifier: MIT
 * Native NPU register leaves 0x10205600/0c/e4. Direct implementation of
 * the common bit helper instructions at 0x102055c0 and 0x102055dc.
 */
#include <stdint.h>

void gx8002_xip_npu_disable_10205600(uint32_t base)
{
    volatile uint32_t *const register_word =
        (volatile uint32_t *)(uintptr_t)base;
    *register_word &= ~UINT32_C(1);
}

uint32_t gx8002_xip_npu_is_enabled_1020560c(uint32_t base)
{
    return *(volatile uint32_t *)(uintptr_t)base & 1u;
}

uint32_t gx8002_xip_npu_all_idle_102056e4(uint32_t base)
{
    return (*(volatile uint32_t *)(uintptr_t)(base + 12u) >> 31u) & 1u;
}
