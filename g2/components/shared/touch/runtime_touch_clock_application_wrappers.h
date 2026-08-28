/* SPDX-License-Identifier: MIT */
#ifndef OPEN_CFW_RUNTIME_TOUCH_CLOCK_APPLICATION_WRAPPERS_H
#define OPEN_CFW_RUNTIME_TOUCH_CLOCK_APPLICATION_WRAPPERS_H

#include <stdint.h>

typedef struct open_cfw_touch_clock_register_view {
    volatile uint32_t *divider_control;
    volatile uint32_t *clock_select_control;
    volatile uint32_t *path_control;
} open_cfw_touch_clock_register_view;

typedef struct open_cfw_touch_clock_state {
    uint32_t frequency_hz;
    uint8_t megahertz_ceiling;
    uint32_t kilohertz_ceiling;
    uint32_t scaled_kilohertz;
} open_cfw_touch_clock_state;

typedef struct open_cfw_touch_clock_provider {
    uint32_t (*set_divider)(void *context, uint32_t divider);
    void (*fault)(void *context, uint32_t reason);
    void (*set_power_mode)(void *context, uint32_t mode);
    void (*delay)(void *context, uint32_t count);
    void (*select_clock)(void *context, uint32_t selection);
    uint32_t (*measure)(void *context);
    void *context;
} open_cfw_touch_clock_provider;

typedef struct open_cfw_touch_application_provider {
    uint32_t (*preflight)(void *context, void *object);
    void (*reset)(void *context, void *object);
    uint32_t (*status)(void *context, void *object);
    void (*finalize)(void *context, void *object);
    uint32_t (*object_exists)(void *context, uint32_t index, void *object);
    uint32_t (*process_object)(void *context, uint32_t index, void *object);
    void (*update_pointer)(void *context, uint32_t index, void *object);
    void *context;
} open_cfw_touch_application_provider;

void open_cfw_touch_clock_12ac_validate(
    const open_cfw_touch_clock_register_view *registers,
    const open_cfw_touch_clock_provider *provider);
void open_cfw_touch_clock_1434_calibrate(
    uint32_t divider_control,
    open_cfw_touch_clock_state *state,
    const open_cfw_touch_clock_provider *provider);
void open_cfw_touch_clock_12d0_transition(
    const open_cfw_touch_clock_register_view *registers,
    open_cfw_touch_clock_state *state,
    const open_cfw_touch_clock_provider *provider);

uint32_t open_cfw_touch_application_17be_preflight(
    void *object, uint8_t *initialized,
    const open_cfw_touch_application_provider *provider);
uint32_t open_cfw_touch_application_1904_process_three(
    void *object, const uint8_t *object_records, uint32_t record_stride,
    const open_cfw_touch_application_provider *provider);
void open_cfw_touch_application_1c54_update_three(
    void *object, const open_cfw_touch_application_provider *provider);

#endif
