/* SPDX-License-Identifier: MIT
 * Native XIP 0x10205950..0x10205995, literal 0x10205998=0x20027350.
 * Direct disassembly proves the six ordered register-helper calls and
 * their constants. Helper bodies are separate authentic source units.
 */
#include <stdint.h>

extern void gx8002_xip_npu_set_clock_gate_10205618(uint32_t, uint32_t);
extern void gx8002_xip_npu_set_idle_cycle_10205648(uint32_t, uint32_t);
extern void gx8002_xip_npu_set_idle_mode_10205630(uint32_t, uint32_t);
extern void gx8002_xip_npu_clear_interrupt_10205768(uint32_t, uint32_t);
extern void gx8002_xip_npu_enable_interrupt_1020566c(uint32_t, uint32_t);
extern void gx8002_xip_npu_set_overtime_10205660(uint32_t, uint32_t);

void gx8002_xip_npu_registers_initialize_10205950(void)
{
    volatile const uint32_t *const control =
        (volatile const uint32_t *)(uintptr_t)UINT32_C(0x20027350);
    gx8002_xip_npu_set_clock_gate_10205618(control[0x171u], 1u);
    gx8002_xip_npu_set_idle_cycle_10205648(control[0x171u], 2000u);
    gx8002_xip_npu_set_idle_mode_10205630(control[0x171u], 0u);
    gx8002_xip_npu_clear_interrupt_10205768(control[0x171u], 0x6fu);
    gx8002_xip_npu_enable_interrupt_1020566c(control[0x171u], 0x6du);
    gx8002_xip_npu_set_overtime_10205660(control[0x171u], 0x100000u);
}
