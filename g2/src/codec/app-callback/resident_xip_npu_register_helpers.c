/* SPDX-License-Identifier: MIT
 * Native XIP 0x102055dc/ec/f0, 0x10205618/30/48/60/6c,
 * 0x10205768. Direct C-SKY instructions establish every register bit
 * and the seven ordered per-interrupt writes. The matching bit-set
 * helper 0x102055cc is sourced in resident_xip_npu_reset.c.
 */
#include <stdint.h>

extern void gx8002_xip_register_set_bit_102055cc(uint32_t, uint32_t);

void gx8002_xip_register_clear_bit_102055dc(uint32_t address, uint32_t bit)
{
    volatile uint32_t *const reg = (volatile uint32_t *)(uintptr_t)address;
    *reg = *reg & ~(1u << (bit & 31u));
}

uint32_t gx8002_xip_register_read_102055ec(uint32_t address)
{
    return *(volatile uint32_t *)(uintptr_t)address;
}

void gx8002_xip_register_write_102055f0(uint32_t address, uint32_t value)
{
    *(volatile uint32_t *)(uintptr_t)address = value;
}

void gx8002_xip_npu_set_clock_gate_10205618(uint32_t base, uint32_t enabled)
{
    if (enabled != 0u) gx8002_xip_register_set_bit_102055cc(base, 12u);
    else gx8002_xip_register_clear_bit_102055dc(base, 12u);
}

void gx8002_xip_npu_set_idle_mode_10205630(uint32_t base, uint32_t enabled)
{
    if (enabled == 0u) gx8002_xip_register_set_bit_102055cc(base, 4u);
    else gx8002_xip_register_clear_bit_102055dc(base, 4u);
}

void gx8002_xip_npu_set_idle_cycle_10205648(uint32_t base, uint32_t cycles)
{
    uint32_t old = gx8002_xip_register_read_102055ec(base);
    gx8002_xip_register_write_102055f0(
        base, (old & 0xffffu) | (cycles << 16u));
}

void gx8002_xip_npu_set_overtime_10205660(uint32_t base, uint32_t cycles)
{
    gx8002_xip_register_write_102055f0(base + 0x14u, cycles);
}

static void interrupt_bits(uint32_t register_address, uint32_t mask)
{
    static const uint8_t shifts[7] = {0u, 4u, 8u, 12u, 13u, 14u, 16u};
    for (uint32_t bit = 0u; bit < 7u; ++bit)
        if ((mask & (1u << bit)) != 0u)
            gx8002_xip_register_set_bit_102055cc(register_address, shifts[bit]);
}

void gx8002_xip_npu_enable_interrupt_1020566c(uint32_t base, uint32_t mask)
{
    interrupt_bits(base + 4u, mask);
}

void gx8002_xip_npu_clear_interrupt_10205768(uint32_t base, uint32_t mask)
{
    interrupt_bits(base + 8u, mask);
}
