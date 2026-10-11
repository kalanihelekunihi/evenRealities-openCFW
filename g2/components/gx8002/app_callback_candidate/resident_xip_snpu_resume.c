/* SPDX-License-Identifier: MIT
 * Native XIP 0x1020599c..0x102059e1, direct branch/register evidence.
 * SRAM state literal 0x102059e4 resolves to 0x20027350. Clock and NPU
 * enable/status lowers are selected source; reset/register init remain
 * genuine separate bodies.
 */
#include <stdint.h>

extern void gx8002_resident_clock_snpu_enable_251ec(uint32_t);
extern uint32_t gx8002_xip_npu_is_enabled_1020560c(uint32_t);
extern void gx8002_xip_npu_disable_10205600(uint32_t);
extern uint32_t gx8002_xip_npu_all_idle_102056e4(uint32_t);
extern void gx8002_xip_npu_reset_10205880(uint32_t);
extern void gx8002_xip_npu_registers_initialize_10205950(void);

uint32_t gx8002_xip_snpu_resume_internal_1020599c(void)
{
    volatile uint32_t *const control =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0x20027350);
    control[0] = 0u;
    control[0x170u] = 0u;
    control[0x174u] = 0u;
    gx8002_resident_clock_snpu_enable_251ec(1u);
    uint32_t npu = control[0x171u];
    if (gx8002_xip_npu_is_enabled_1020560c(npu) != 0u) {
        gx8002_xip_npu_disable_10205600(npu);
        while (gx8002_xip_npu_all_idle_102056e4(npu) == 0u) {}
    }
    gx8002_xip_npu_reset_10205880(control[0x172u]);
    gx8002_xip_npu_registers_initialize_10205950();
    return 0u;
}
