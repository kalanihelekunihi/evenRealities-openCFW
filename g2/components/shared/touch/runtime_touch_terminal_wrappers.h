/* SPDX-License-Identifier: MIT */
#ifndef OPENCFW_TOUCH_TERMINAL_WRAPPERS_H
#define OPENCFW_TOUCH_TERMINAL_WRAPPERS_H

#include <stdint.h>

typedef struct {
    uint8_t *object;
    uint32_t *control;
} open_cfw_touch_terminal_context;

typedef struct {
    void (*reset_object)(void *provider_context, uint32_t index,
                         open_cfw_touch_terminal_context *context);
    uint32_t (*capsense_call)(void *provider_context, uint32_t argument0,
                              uint32_t argument1, uint32_t argument2);
    void *context;
} open_cfw_touch_terminal_provider;

uint32_t open_cfw_touch_terminal_1368_passthrough(uint32_t value);
void open_cfw_touch_terminal_25f8_reset_three(
    open_cfw_touch_terminal_context *context,
    const open_cfw_touch_terminal_provider *provider);
uint32_t open_cfw_touch_terminal_2972_provider_call(
    const open_cfw_touch_terminal_provider *provider,
    uint32_t argument0,
    uint32_t argument1,
    uint32_t argument2);
uint32_t open_cfw_touch_terminal_297a_conditional_call(
    const open_cfw_touch_terminal_provider *provider,
    uint32_t value);

#endif
