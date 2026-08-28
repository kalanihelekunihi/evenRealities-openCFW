/* SPDX-License-Identifier: MIT */
#include <stdint.h>

#include "../../components/shared/case/runtime_case_register_primitives.c"

uint32_t open_cfw_test_case_register_primitives(void)
{
    uint32_t state[17] = {0U};
    const volatile uint32_t *handle_value = state;
    const volatile uint32_t *const *handle = &handle_value;
    uint32_t result = 0U;

    state[16] = UINT32_C(0x12345678);
    result |= open_cfw_case_handle_word16(handle) == UINT32_C(0x12345678)
                  ? UINT32_C(1) : UINT32_C(0);

    state[4] = UINT32_C(0xA0);
    result |= open_cfw_case_register_any_bits(state, UINT32_C(0x20)) != 0U
                  ? UINT32_C(2) : UINT32_C(0);
    result |= open_cfw_case_register_any_bits(state, UINT32_C(0x04)) == 0U
                  ? UINT32_C(4) : UINT32_C(0);

    open_cfw_case_register_write_channel(state, UINT32_C(0x1111), 1U);
    open_cfw_case_register_write_channel(state, UINT32_C(0x2222), 0U);
    result |= state[6] == UINT32_C(0x1111) &&
                      state[10] == UINT32_C(0x2222)
                  ? UINT32_C(8) : UINT32_C(0);

    state[2] = UINT32_C(0x15);
    result |= open_cfw_case_tick_word2(state) == UINT32_C(0x15) &&
                      open_cfw_case_status_word2_bit0(state) == 1U &&
                      open_cfw_case_status_word2_bit0_alias(state) == 1U &&
                      open_cfw_case_status_word2_bit2(state) == 1U
                  ? UINT32_C(0x10) : UINT32_C(0);

    state[3] = 0U;
    result |= open_cfw_case_status_word3_field10_clear(state) == 1U
                  ? UINT32_C(0x20) : UINT32_C(0);
    state[3] = UINT32_C(1) << 10;
    result |= open_cfw_case_status_word3_field10_clear(state) == 0U
                  ? UINT32_C(0x40) : UINT32_C(0);

    state[4] = UINT32_C(0x4444);
    state[5] = UINT32_C(0x5555);
    state[6] = UINT32_C(0x6666);
    result |= open_cfw_case_device_info_word4(state) == UINT32_C(0x4444) &&
                      open_cfw_case_device_info_word5(state) == UINT32_C(0x5555) &&
                      open_cfw_case_device_info_word6(state) == UINT32_C(0x6666)
                  ? UINT32_C(0x80) : UINT32_C(0);

    state[8] = UINT32_C(0x077F60AA);
    result |= open_cfw_case_flash_status_classify(state) == UINT32_C(0xAA) &&
                      open_cfw_case_flash_status_masked(state) ==
                          UINT32_C(0x077F6000)
                  ? UINT32_C(0x100) : UINT32_C(0);
    state[8] = UINT32_C(0x45);
    result |= open_cfw_case_flash_status_classify(state) == UINT32_C(0xBB)
                  ? UINT32_C(0x200) : UINT32_C(0);

    return result;
}

uint32_t open_cfw_test_case_register_null_guards(void)
{
    open_cfw_case_register_write_channel((volatile uint32_t *)0, 1U, 1U);
    return open_cfw_case_handle_word16((const volatile uint32_t *const *)0) |
           open_cfw_case_register_any_bits((const volatile uint32_t *)0, 1U) |
           open_cfw_case_tick_word2((const volatile uint32_t *)0) |
           open_cfw_case_device_info_word4((const volatile uint32_t *)0) |
           open_cfw_case_device_info_word5((const volatile uint32_t *)0) |
           open_cfw_case_device_info_word6((const volatile uint32_t *)0) |
           open_cfw_case_status_word2_bit0((const volatile uint32_t *)0) |
           open_cfw_case_status_word2_bit0_alias((const volatile uint32_t *)0) |
           open_cfw_case_status_word2_bit2((const volatile uint32_t *)0) |
           open_cfw_case_status_word3_field10_clear((const volatile uint32_t *)0) |
           open_cfw_case_flash_status_classify((const volatile uint32_t *)0) |
           open_cfw_case_flash_status_masked((const volatile uint32_t *)0);
}
