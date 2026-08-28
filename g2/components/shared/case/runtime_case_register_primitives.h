/* SPDX-License-Identifier: MIT */
#ifndef OPEN_CFW_RUNTIME_CASE_REGISTER_PRIMITIVES_H
#define OPEN_CFW_RUNTIME_CASE_REGISTER_PRIMITIVES_H

#include <stdint.h>

#define OPEN_CFW_CASE_FLASH_STATUS_MASK UINT32_C(0x077F6000)

uint32_t open_cfw_case_handle_word16(
    const volatile uint32_t *const *handle);
uint32_t open_cfw_case_register_any_bits(
    const volatile uint32_t *registers, uint32_t mask);
void open_cfw_case_register_write_channel(
    volatile uint32_t *registers, uint32_t value, uint32_t alternate);
uint32_t open_cfw_case_tick_word2(const volatile uint32_t *state);
uint32_t open_cfw_case_device_info_word4(const volatile uint32_t *state);
uint32_t open_cfw_case_device_info_word5(const volatile uint32_t *state);
uint32_t open_cfw_case_device_info_word6(const volatile uint32_t *state);
uint32_t open_cfw_case_status_word2_bit0(const volatile uint32_t *state);
uint32_t open_cfw_case_status_word2_bit0_alias(const volatile uint32_t *state);
uint32_t open_cfw_case_status_word2_bit2(const volatile uint32_t *state);
uint32_t open_cfw_case_status_word3_field10_clear(
    const volatile uint32_t *state);
uint32_t open_cfw_case_flash_status_classify(
    const volatile uint32_t *flash_registers);
uint32_t open_cfw_case_flash_status_masked(
    const volatile uint32_t *flash_registers);

#endif
