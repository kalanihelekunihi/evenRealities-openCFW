/*
 * SPDX-License-Identifier: MIT
 *
 * Clean-room charging-case register-field primitives. Fixed-address stock
 * accesses are represented by caller-supplied volatile register views. This
 * unit therefore cannot execute MMIO unless an authorized platform adapter
 * explicitly supplies an MMIO address.
 */
#include <stddef.h>
#include <stdint.h>

#include "runtime_case_register_primitives.h"

uint32_t open_cfw_case_handle_word16(
    const volatile uint32_t *const *handle)
{
    if (handle == NULL || *handle == NULL) {
        return 0U;
    }
    return (*handle)[16];
}

uint32_t open_cfw_case_register_any_bits(
    const volatile uint32_t *registers, uint32_t mask)
{
    if (registers == NULL) {
        return 0U;
    }
    return (registers[4] & mask) != 0U ? 1U : 0U;
}

void open_cfw_case_register_write_channel(
    volatile uint32_t *registers, uint32_t value, uint32_t alternate)
{
    if (registers == NULL) {
        return;
    }
    registers[alternate != 0U ? 6U : 10U] = value;
}

uint32_t open_cfw_case_tick_word2(const volatile uint32_t *state)
{
    return state == NULL ? 0U : state[2];
}

uint32_t open_cfw_case_device_info_word4(const volatile uint32_t *state)
{
    return state == NULL ? 0U : state[4];
}

uint32_t open_cfw_case_device_info_word5(const volatile uint32_t *state)
{
    return state == NULL ? 0U : state[5];
}

uint32_t open_cfw_case_device_info_word6(const volatile uint32_t *state)
{
    return state == NULL ? 0U : state[6];
}

uint32_t open_cfw_case_status_word2_bit0(const volatile uint32_t *state)
{
    return state == NULL ? 0U : state[2] & 1U;
}

uint32_t open_cfw_case_status_word2_bit0_alias(const volatile uint32_t *state)
{
    return open_cfw_case_status_word2_bit0(state);
}

uint32_t open_cfw_case_status_word2_bit2(const volatile uint32_t *state)
{
    return state == NULL ? 0U : (state[2] >> 2) & 1U;
}

uint32_t open_cfw_case_status_word3_field10_clear(
    const volatile uint32_t *state)
{
    if (state == NULL) {
        return 0U;
    }
    return ((state[3] >> 10) & 3U) == 0U ? 1U : 0U;
}

uint32_t open_cfw_case_flash_status_classify(
    const volatile uint32_t *flash_registers)
{
    uint32_t value;

    if (flash_registers == NULL) {
        return 0U;
    }
    value = flash_registers[8] & UINT32_C(0xFF);
    if (value != UINT32_C(0xAA) && value != UINT32_C(0xCC)) {
        value = UINT32_C(0xBB);
    }
    return value;
}

uint32_t open_cfw_case_flash_status_masked(
    const volatile uint32_t *flash_registers)
{
    if (flash_registers == NULL) {
        return 0U;
    }
    return flash_registers[8] & OPEN_CFW_CASE_FLASH_STATUS_MASK;
}
