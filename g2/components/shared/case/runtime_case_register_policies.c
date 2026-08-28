/*
 * SPDX-License-Identifier: MIT
 *
 * Clean-room charging-case register and state policies.  Every register view
 * is supplied by the caller: this unit embeds no fixed peripheral address and
 * cannot independently select or access an MMIO device.
 */
#include "runtime_case_register_policies.h"

#include <stddef.h>


static void instruction_barrier(void)
{
#if defined(__arm__) || defined(__thumb__)
    __asm__ volatile("isb" ::: "memory");
#else
    __asm__ volatile("" ::: "memory");
#endif
}


void open_cfw_case_gpio_policy_update(
    volatile uint32_t *registers, uint32_t preserve_mask,
    uint32_t fixed_set_mask, int mode, uint32_t selection)
{
    uint32_t value;
    if (registers == NULL) return;
    value = registers[5] & preserve_mask;
    value = mode == 4 ? value & ~UINT32_C(0x2000)
                      : value | UINT32_C(0x2000);
    registers[5] = (selection << 3U) | value | fixed_set_mask;
}


void open_cfw_case_register_pair_commit(
    volatile uint32_t *registers, uint32_t output[2],
    uint32_t first, uint32_t second)
{
    if (registers == NULL || output == NULL) return;
    registers[5] |= 1U;
    output[0] = first;
    instruction_barrier();
    output[1] = second;
}


bool open_cfw_case_flag31_set(volatile uint32_t *registers)
{
    if (registers == NULL) return false;
    registers[5] |= UINT32_C(0x80000000);
    return (registers[5] & UINT32_C(0x80000000)) == 0U;
}


uint32_t open_cfw_case_flag27_set(volatile uint32_t *registers)
{
    if (registers == NULL) return 0U;
    registers[5] |= UINT32_C(0x08000000);
    return 1U;
}


bool open_cfw_case_flag30_set(volatile uint32_t *registers)
{
    if (registers == NULL) return false;
    registers[5] |= UINT32_C(0x40000000);
    return (registers[5] & UINT32_C(0x40000000)) == 0U;
}


void open_cfw_case_interrupt_enable(
    volatile uint32_t *set_enable_register, int32_t interrupt_number)
{
    if (set_enable_register != NULL && interrupt_number >= 0) {
        *set_enable_register = UINT32_C(1) << ((uint32_t)interrupt_number & 31U);
    }
}


void open_cfw_case_clock_descriptor(
    uint32_t output[4], uint32_t clock_configuration,
    uint32_t selector_register, uint32_t *selector)
{
    if (output == NULL || selector == NULL) return;
    output[0] = 7U;
    output[1] = clock_configuration & 7U;
    output[2] = clock_configuration & UINT32_C(0x0F00);
    output[3] = clock_configuration & UINT32_C(0x7000);
    *selector = selector_register & 7U;
}


bool open_cfw_case_validate_magic_state(
    uint8_t state[4], volatile uint8_t *magic_output)
{
    uint16_t count;
    bool valid;
    if (state == NULL || magic_output == NULL) return false;
    count = (uint16_t)state[2] | ((uint16_t)state[3] << 8U);
    valid = count >= 2U && state[1] == (uint8_t)'Z';
    if (valid) *magic_output = 0x5AU;
    state[2] = valid ? 1U : 0U;
    state[3] = 0U;
    return valid;
}
