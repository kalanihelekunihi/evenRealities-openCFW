/* SPDX-License-Identifier: MIT */
/* Recovered initialization call sequence. This external view describes only
 * the observed pointer slot, not ownership of the surrounding driver state. */
#include <stdint.h>
extern void *volatile open_cfw_gx8002_snpu_register_pointer;
extern void open_cfw_gx8002_npu_set_clock_gate(void *, uint32_t);
extern void open_cfw_gx8002_npu_set_idle_cycle(void *, uint32_t);
extern void open_cfw_gx8002_npu_set_idle_mode(void *, uint32_t);
extern void open_cfw_gx8002_npu_clr_interrupt(void *, uint32_t);
extern void open_cfw_gx8002_npu_en_interrupt(void *, uint32_t);
extern void open_cfw_gx8002_npu_set_overtime_thr(void *, uint32_t);
void open_cfw_gx8002_npu_regs_init(void)
{
    open_cfw_gx8002_npu_set_clock_gate(open_cfw_gx8002_snpu_register_pointer, 1);
    open_cfw_gx8002_npu_set_idle_cycle(open_cfw_gx8002_snpu_register_pointer, 2000);
    open_cfw_gx8002_npu_set_idle_mode(open_cfw_gx8002_snpu_register_pointer, 0);
    open_cfw_gx8002_npu_clr_interrupt(open_cfw_gx8002_snpu_register_pointer, 111);
    open_cfw_gx8002_npu_en_interrupt(open_cfw_gx8002_snpu_register_pointer, 109);
    open_cfw_gx8002_npu_set_overtime_thr(open_cfw_gx8002_snpu_register_pointer, 0x100000);
}
