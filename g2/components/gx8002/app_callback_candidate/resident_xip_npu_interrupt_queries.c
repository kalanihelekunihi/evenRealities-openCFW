/* SPDX-License-Identifier: MIT
 * Image-A XIP native NPU interrupt and address query bodies at
 * 0x102056f0, 0x102057e0, and 0x10205838..0x102058c4.
 * Register access uses already selected native read/set-bit lowers.
 */
#include <stdint.h>

extern uint32_t gx8002_xip_register_read_102055ec(uint32_t address);
extern void gx8002_xip_register_set_bit_102055cc(
    uint32_t address, uint32_t bit);

void gx8002_xip_npu_get_interrupt_102056f0(
    uint32_t base, uint32_t *result)
{
    uint32_t value = gx8002_xip_register_read_102055ec(base + 0x0cu);
    uint32_t mask = value & 1u;
    if (value & 0x10u) mask |= 2u;
    if (value & 0x100u) mask |= 4u;
    if (value & 0x1000u) mask |= 8u;
    if (value & 0x2000u) mask |= 0x10u;
    if (value & 0x4000u) mask |= 0x20u;
    if (value & 0x10000u) mask |= 0x40u;
    *result = mask;
}

void gx8002_xip_npu_clear_without_overflow_102057e0(
    uint32_t base, uint32_t mask)
{
    if (mask & 1u) gx8002_xip_register_set_bit_102055cc(base + 8u, 0u);
    if (mask & 2u) gx8002_xip_register_set_bit_102055cc(base + 8u, 4u);
    if (mask & 4u) gx8002_xip_register_set_bit_102055cc(base + 8u, 8u);
    if (mask & 8u) gx8002_xip_register_set_bit_102055cc(base + 8u, 12u);
    if (mask & 0x40u) gx8002_xip_register_set_bit_102055cc(base + 8u, 16u);
}

void gx8002_xip_npu_clear_overflow_10205838(uint32_t base, uint32_t mask)
{
    if (mask & 0x10u) gx8002_xip_register_set_bit_102055cc(base + 8u, 13u);
    if (mask & 0x20u) gx8002_xip_register_set_bit_102055cc(base + 8u, 14u);
}

void gx8002_xip_npu_get_overflow_command_10205870(
    uint32_t base, uint32_t *result)
{
    *result = gx8002_xip_register_read_102055ec(base + 0x124u);
}

void gx8002_xip_npu_get_task_head_102058a4(
    uint32_t base, uint32_t *result)
{
    *result = gx8002_xip_register_read_102055ec(base + 0x10u);
}

void gx8002_xip_npu_get_base_address_102058b4(
    uint32_t base, uint32_t index, uint32_t *result)
{
    *result = gx8002_xip_register_read_102055ec(base + index * 4u);
}

void gx8002_xip_npu_get_current_command_102058c4(
    uint32_t base, uint32_t *result)
{
    *result = gx8002_xip_register_read_102055ec(base + 0x100u);
}
