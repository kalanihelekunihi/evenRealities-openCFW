/* SPDX-License-Identifier: MIT */
#ifndef OPENCFW_TOUCH_STARTUP_CLOSED_H
#define OPENCFW_TOUCH_STARTUP_CLOSED_H

#include <stdint.h>

typedef struct {
    uint8_t bytes[80];
} open_cfw_touch_startup_record;

typedef struct {
    void (*disable_divider)(void *context, uint32_t type, uint32_t index);
    void (*set_integer_divider)(void *context, uint32_t type, uint32_t index,
                                uint32_t divider);
    void (*set_fractional_divider)(void *context, uint32_t type,
                                   uint32_t index, uint32_t divider,
                                   uint32_t fraction);
    void (*enable_divider)(void *context, uint32_t type, uint32_t index);
    void (*assign_divider)(void *context, uint32_t destination,
                           uint32_t type, uint32_t index);
    void *context;
} open_cfw_touch_startup_clock_provider;

void open_cfw_touch_startup_0d4c_initialize(
    open_cfw_touch_startup_record *record,
    const uint16_t *initial_timeout);
void open_cfw_touch_startup_11b4_passthrough_sequence(void);
void open_cfw_touch_startup_11d0_configure_dividers(
    const open_cfw_touch_startup_clock_provider *provider);
void open_cfw_touch_startup_1228_assign_divider(
    const open_cfw_touch_startup_clock_provider *provider);

#endif
