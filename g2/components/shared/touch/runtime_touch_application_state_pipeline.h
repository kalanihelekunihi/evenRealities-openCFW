/* SPDX-License-Identifier: MIT */
#ifndef OPENCFW_TOUCH_APPLICATION_STATE_PIPELINE_H
#define OPENCFW_TOUCH_APPLICATION_STATE_PIPELINE_H

#include <stdint.h>

uint32_t open_cfw_touch_state_1ebc_pack(
    const uint8_t *selector, uint8_t *output, const uint8_t *context);
void open_cfw_touch_state_16d4_copy8(
    uint32_t flags, const uint8_t *source, uint8_t *destination);
void open_cfw_touch_state_16e6_blend_pair(
    const uint8_t *config, uint8_t *current, uint8_t *history);
void open_cfw_touch_state_172a_sync_records(
    const uint8_t *control, uint8_t *object);
void open_cfw_touch_state_2568_reset_object(
    uint32_t object_index, const uint8_t *context);
void open_cfw_touch_state_270a_update_lanes(uint8_t *context);
void open_cfw_touch_state_28c0_cap_object(
    uint32_t object_index, const uint8_t *context);
void open_cfw_touch_state_2902_cap_enabled_object(
    uint32_t object_index, const uint8_t *context);
void open_cfw_touch_state_291e_cap_record(
    uint32_t object_index, uint32_t record_index, const uint8_t *context);
void open_cfw_touch_state_2956_cap_enabled_record(
    uint32_t object_index, uint32_t record_index, const uint8_t *context);
uint32_t open_cfw_touch_state_298e_status80(const uint8_t *context);

#endif
