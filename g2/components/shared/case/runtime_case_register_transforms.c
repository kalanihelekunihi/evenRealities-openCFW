/*
 * SPDX-License-Identifier: MIT
 *
 * Clean-room charging-case register transforms. The register view is always
 * supplied by the caller; this unit embeds no device address and cannot
 * independently execute MMIO.
 */
#include <stddef.h>
#include <stdint.h>

#include "runtime_case_register_transforms.h"

void open_cfw_case_control_word5_set(
    volatile uint32_t *registers, uint32_t value)
{
    if (registers == NULL) {
        return;
    }
    registers[5] |= value | (UINT32_C(1) << 16);
}

void open_cfw_case_flash_control_update(
    volatile uint32_t *registers, uint32_t clear_mask,
    uint32_t set_bits_1, uint32_t set_bits_2)
{
    if (registers == NULL) {
        return;
    }
    registers[8] = (registers[8] & ~(clear_mask | UINT32_C(0xFF))) |
                   set_bits_1 | set_bits_2;
}

void open_cfw_case_control_word0_replace_field22(
    volatile uint32_t *registers, uint32_t value)
{
    if (registers == NULL) {
        return;
    }
    registers[0] = (registers[0] & ~(UINT32_C(7) << 22)) | value;
}

void open_cfw_case_control_word5_replace_slot(
    volatile uint32_t *registers, uint32_t selector, uint32_t value)
{
    uint32_t shift;

    if (registers == NULL) {
        return;
    }
    shift = selector & UINT32_C(4);
    registers[5] = (registers[5] & ~(UINT32_C(7) << shift)) |
                   (value << shift);
}

int32_t open_cfw_case_sign_extend_u16(uint32_t value)
{
    uint32_t low = value & UINT32_C(0xFFFF);

    if ((low & UINT32_C(0x8000)) != 0U) {
        return -(int32_t)((UINT32_C(0x10000) - low) & UINT32_C(0xFFFF));
    }
    return (int32_t)low;
}
