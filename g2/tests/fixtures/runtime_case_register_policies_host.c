/* SPDX-License-Identifier: MIT */
#include "runtime_case_register_policies.h"

#include <stdint.h>

static int test_gpio_policy(void)
{
    uint32_t registers[8] = {0};

    registers[5] = 0xFFFFFFFFU;
    open_cfw_case_gpio_policy_update(registers, 0xFFFF0000U, 4U, 4, 3U);
    if (registers[5] != 0xFFFF001CU) return 1;

    registers[5] = UINT32_C(0xA5A55A5A);
    open_cfw_case_gpio_policy_update(
        registers, UINT32_C(0xFF0000FF), UINT32_C(0x00040000), 3,
        UINT32_C(0x12345678));
    if (registers[5] != UINT32_C(0xB5A6B3DA)) return 2;
    return 0;
}

static int test_register_writes(void)
{
    uint32_t registers[8] = {0U};
    uint32_t output[2] = {0U, 0U};
    uint32_t interrupt = UINT32_C(0xA5A5A5A5);

    open_cfw_case_register_pair_commit(registers, output, 7U, 9U);
    if (output[0] != 7U || output[1] != 9U || registers[5] != 1U) return 1;
    registers[5] = 0U;
    if (open_cfw_case_flag31_set(registers) ||
        registers[5] != UINT32_C(0x80000000)) return 2;
    registers[5] = 0U;
    if (open_cfw_case_flag27_set(registers) != 1U ||
        registers[5] != UINT32_C(0x08000000)) return 3;
    registers[5] = 0U;
    if (open_cfw_case_flag30_set(registers) ||
        registers[5] != UINT32_C(0x40000000)) return 4;

    open_cfw_case_interrupt_enable(&interrupt, -1);
    if (interrupt != UINT32_C(0xA5A5A5A5)) return 5;
    open_cfw_case_interrupt_enable(&interrupt, 5);
    if (interrupt != UINT32_C(0x20)) return 6;
    open_cfw_case_interrupt_enable(&interrupt, 31);
    if (interrupt != UINT32_C(0x80000000)) return 7;
    open_cfw_case_interrupt_enable(&interrupt, 32);
    if (interrupt != 1U) return 8;
    return 0;
}

static int test_descriptors_and_state(void)
{
    uint32_t output[4] = {0U, 0U, 0U, 0U};
    uint32_t selector = 0U;
    uint8_t state[4] = {0U, 'Z', 2U, 0U};
    uint8_t magic = 0U;

    open_cfw_case_clock_descriptor(output, 0x7507U, 6U, &selector);
    if (output[0] != 7U || output[1] != 7U || output[2] != 0x500U ||
        output[3] != 0x7000U || selector != 6U) return 1;
    if (!open_cfw_case_validate_magic_state(state, &magic) || magic != 0x5AU ||
        state[2] != 1U || state[3] != 0U) return 2;

    state[1] = 'Z'; state[2] = 1U; state[3] = 0U; magic = 0xC3U;
    if (open_cfw_case_validate_magic_state(state, &magic) || magic != 0xC3U ||
        state[2] != 0U || state[3] != 0U) return 3;
    state[1] = 'D'; state[2] = 2U; state[3] = 0U;
    if (open_cfw_case_validate_magic_state(state, &magic) ||
        state[2] != 0U || state[3] != 0U) return 4;
    return 0;
}

static int test_null_views(void)
{
    open_cfw_case_gpio_policy_update((volatile uint32_t *)0, 0U, 0U, 0, 0U);
    open_cfw_case_register_pair_commit(
        (volatile uint32_t *)0, (uint32_t *)0, 0U, 0U);
    if (open_cfw_case_flag31_set((volatile uint32_t *)0)) return 1;
    if (open_cfw_case_flag27_set((volatile uint32_t *)0) != 0U) return 2;
    if (open_cfw_case_flag30_set((volatile uint32_t *)0)) return 3;
    open_cfw_case_interrupt_enable((volatile uint32_t *)0, 0);
    open_cfw_case_clock_descriptor((uint32_t *)0, 0U, 0U, (uint32_t *)0);
    if (open_cfw_case_validate_magic_state((uint8_t *)0,
                                           (volatile uint8_t *)0)) return 4;
    return 0;
}

int main(void)
{
    int result = test_gpio_policy();
    if (result != 0) return 10 + result;
    result = test_register_writes();
    if (result != 0) return 20 + result;
    result = test_descriptors_and_state();
    if (result != 0) return 30 + result;
    result = test_null_views();
    if (result != 0) return 40 + result;
    return 0;
}
