/* SPDX-License-Identifier: MIT */
/* Reconstructed NPU register configuration; candidate pending qualification. */
#include <stdint.h>
extern uint32_t open_cfw_gx8002_reg_get_value(volatile uint32_t *);
extern void open_cfw_gx8002_reg_set_value(volatile uint32_t *, uint32_t);
extern void open_cfw_gx8002_reg_set_bit(volatile uint32_t *, uint32_t);
extern void open_cfw_gx8002_reg_clear_bit(volatile uint32_t *, uint32_t);
void open_cfw_gx8002_npu_set_clock_gate(void *base, uint32_t enabled)
{
    if (enabled)
        open_cfw_gx8002_reg_set_bit(base, 12);
    else
        open_cfw_gx8002_reg_clear_bit(base, 12);
}
void open_cfw_gx8002_npu_set_idle_mode(void *base, uint32_t mode)
{
    if (mode == 0)
        open_cfw_gx8002_reg_set_bit(base, 4);
    else
        open_cfw_gx8002_reg_clear_bit(base, 4);
}
void open_cfw_gx8002_npu_set_idle_cycle(void *base, uint32_t cycles)
{
    uint32_t value = open_cfw_gx8002_reg_get_value(base);
    open_cfw_gx8002_reg_set_value(base, (value & UINT32_C(0xffff)) | (cycles << 16));
}
void open_cfw_gx8002_npu_set_overtime_thr(void *base, uint32_t threshold)
{
    open_cfw_gx8002_reg_set_value((volatile uint32_t *)((uintptr_t)base + 20u), threshold);
}
