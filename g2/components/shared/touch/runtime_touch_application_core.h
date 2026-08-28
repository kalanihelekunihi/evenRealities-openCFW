/* SPDX-License-Identifier: MIT */
#ifndef OPEN_CFW_RUNTIME_TOUCH_APPLICATION_CORE_H
#define OPEN_CFW_RUNTIME_TOUCH_APPLICATION_CORE_H

#include <stdint.h>

typedef struct open_cfw_touch_application_record_view {
    void *algorithm;
    uint8_t *samples;
    uint16_t *auxiliary;
    uint8_t *coefficients;
    uint8_t *mode_bytes;
    uint16_t sample_count;
    uint16_t flags;
    uint8_t mode;
    uint8_t lifecycle;
} open_cfw_touch_application_record_view;

typedef struct open_cfw_touch_application_core_provider {
    open_cfw_touch_application_record_view *(*record_at)(
        void *provider_context, uint32_t index, void *object);
    uint32_t (*object_exists)(
        void *provider_context, uint32_t index, void *object);
    void (*update_pointer)(
        void *provider_context, uint32_t index, void *object);
    void (*selection_update)(
        void *provider_context, open_cfw_touch_application_record_view *record,
        void *object);
    void (*prepare_sample)(
        void *provider_context, open_cfw_touch_application_record_view *record,
        uint8_t *sample, uint8_t *coefficients, uint8_t *mode_byte);
    uint32_t (*process_sample)(
        void *provider_context, void *algorithm, uint8_t *sample,
        uint16_t *auxiliary, void *object);
    void (*finish_sample)(
        void *provider_context, void *algorithm, uint8_t *sample);
    void (*apply_four)(
        void *provider_context, open_cfw_touch_application_record_view *record,
        uint8_t *sample, uint8_t *coefficients);
    void (*apply_two)(
        void *provider_context, open_cfw_touch_application_record_view *record,
        uint8_t *sample, uint8_t *coefficients, uint8_t *mode_byte);
    void (*apply_final)(
        void *provider_context, open_cfw_touch_application_record_view *record,
        uint8_t *sample, uint8_t *coefficients);
    void *provider_context;
} open_cfw_touch_application_core_provider;

typedef struct open_cfw_touch_application_run_provider {
    void (*notify)(void *provider_context, uint32_t event, void *object);
    uint32_t (*preflight)(void *provider_context, void *object);
    uint32_t (*stage_a)(void *provider_context, void *object);
    uint32_t (*stage_b)(void *provider_context, void *object);
    uint32_t (*stage_c)(void *provider_context, void *object);
    uint32_t (*retry_budget)(
        void *provider_context, uint32_t reference_hz,
        uint32_t timebase_megahertz, uint32_t limit);
    uint32_t (*poll)(void *provider_context, void *object);
    void (*update_pointer)(
        void *provider_context, uint32_t index, void *object);
    void (*update_all)(void *provider_context, void *object);
    void (*shutdown)(void *provider_context, void *object);
    void *provider_context;
} open_cfw_touch_application_run_provider;

void open_cfw_touch_application_1b6c_update(
    uint32_t index, void *object,
    const open_cfw_touch_application_core_provider *provider);
uint32_t open_cfw_touch_application_2638_dispatch(
    uint32_t index, void *object,
    const open_cfw_touch_application_core_provider *provider);
uint32_t open_cfw_touch_application_18a8_process(
    uint32_t index, void *object,
    const open_cfw_touch_application_core_provider *provider);
uint32_t open_cfw_touch_application_17f4_run(
    void *object, volatile uint32_t *control_flags, uint8_t *busy,
    uint32_t timebase_hz,
    const open_cfw_touch_application_run_provider *provider);

#endif
