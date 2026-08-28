/* SPDX-License-Identifier: MIT */
#include <stdint.h>

#include "../../components/shared/case/runtime_case_register_transforms.c"

uint32_t open_cfw_test_case_register_transforms(void)
{
    uint32_t registers[9] = {0U};
    uint32_t result = 0U;

    registers[5] = UINT32_C(0x20);
    open_cfw_case_control_word5_set(registers, UINT32_C(0x04));
    result |= registers[5] == UINT32_C(0x10024) ? 1U : 0U;

    registers[8] = UINT32_C(0xFFFFFFFF);
    open_cfw_case_flash_control_update(
        registers, UINT32_C(0x00010000), UINT32_C(0x20), UINT32_C(0x04));
    result |= registers[8] == UINT32_C(0xFFFEFF24) ? 2U : 0U;

    registers[0] = UINT32_C(0xFFFFFFFF);
    open_cfw_case_control_word0_replace_field22(registers, UINT32_C(2) << 22);
    result |= registers[0] == UINT32_C(0xFEBFFFFF) ? 4U : 0U;

    registers[5] = UINT32_C(0xFFFFFFFF);
    open_cfw_case_control_word5_replace_slot(registers, 0U, 2U);
    result |= registers[5] == UINT32_C(0xFFFFFFFA) ? 8U : 0U;
    open_cfw_case_control_word5_replace_slot(registers, 4U, 3U);
    result |= registers[5] == UINT32_C(0xFFFFFFBA) ? 16U : 0U;

    result |= open_cfw_case_sign_extend_u16(UINT32_C(0x7FFF)) == 32767
                  ? 32U : 0U;
    result |= open_cfw_case_sign_extend_u16(UINT32_C(0xFFFF)) == -1
                  ? 64U : 0U;
    result |= open_cfw_case_sign_extend_u16(UINT32_C(0x8000)) == -32768
                  ? 128U : 0U;
    return result;
}

uint32_t open_cfw_test_case_register_transform_null_guards(void)
{
    open_cfw_case_control_word5_set((volatile uint32_t *)0, 1U);
    open_cfw_case_flash_control_update((volatile uint32_t *)0, 1U, 2U, 4U);
    open_cfw_case_control_word0_replace_field22((volatile uint32_t *)0, 1U);
    open_cfw_case_control_word5_replace_slot((volatile uint32_t *)0, 0U, 1U);
    return 0U;
}
