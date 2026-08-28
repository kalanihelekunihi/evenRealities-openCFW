/* SPDX-License-Identifier: MIT */
#ifndef OPENCFW_TOUCH_DEFERRED_WORK_H
#define OPENCFW_TOUCH_DEFERRED_WORK_H

#include <stdint.h>

typedef struct {
    uint8_t notify_pending;
    uint8_t config_pending;
    uint16_t captured_value;
} open_cfw_touch_deferred_state;

typedef struct {
    uint32_t (*enter_critical)(void *context);
    void (*exit_critical)(void *context, uint32_t token);
    void (*notify_value)(void *context, uint16_t value);
    int (*load_configuration)(void *context);
    void *context;
} open_cfw_touch_deferred_provider;

void open_cfw_touch_deferred_0780_process(
    open_cfw_touch_deferred_state *state,
    const open_cfw_touch_deferred_provider *provider);

#endif
