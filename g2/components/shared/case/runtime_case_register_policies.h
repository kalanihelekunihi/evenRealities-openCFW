/* SPDX-License-Identifier: MIT */
#ifndef OPEN_CFW_RUNTIME_CASE_REGISTER_POLICIES_H
#define OPEN_CFW_RUNTIME_CASE_REGISTER_POLICIES_H

#include <stdbool.h>
#include <stdint.h>

void open_cfw_case_gpio_policy_update(
    volatile uint32_t *registers, uint32_t preserve_mask,
    uint32_t fixed_set_mask, int mode, uint32_t selection);
void open_cfw_case_register_pair_commit(
    volatile uint32_t *registers, uint32_t output[2],
    uint32_t first, uint32_t second);
bool open_cfw_case_flag31_set(volatile uint32_t *registers);
uint32_t open_cfw_case_flag27_set(volatile uint32_t *registers);
bool open_cfw_case_flag30_set(volatile uint32_t *registers);
void open_cfw_case_interrupt_enable(
    volatile uint32_t *set_enable_register, int32_t interrupt_number);
void open_cfw_case_clock_descriptor(
    uint32_t output[4], uint32_t clock_configuration,
    uint32_t selector_register, uint32_t *selector);
bool open_cfw_case_validate_magic_state(
    uint8_t state[4], volatile uint8_t *magic_output);

#endif
