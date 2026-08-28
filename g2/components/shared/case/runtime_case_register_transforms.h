/* SPDX-License-Identifier: MIT */
#ifndef OPEN_CFW_RUNTIME_CASE_REGISTER_TRANSFORMS_H
#define OPEN_CFW_RUNTIME_CASE_REGISTER_TRANSFORMS_H

#include <stdint.h>

void open_cfw_case_control_word5_set(
    volatile uint32_t *registers, uint32_t value);
void open_cfw_case_flash_control_update(
    volatile uint32_t *registers, uint32_t clear_mask,
    uint32_t set_bits_1, uint32_t set_bits_2);
void open_cfw_case_control_word0_replace_field22(
    volatile uint32_t *registers, uint32_t value);
void open_cfw_case_control_word5_replace_slot(
    volatile uint32_t *registers, uint32_t selector, uint32_t value);
int32_t open_cfw_case_sign_extend_u16(uint32_t value);

#endif
