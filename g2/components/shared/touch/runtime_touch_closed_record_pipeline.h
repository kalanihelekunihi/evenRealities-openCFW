/* SPDX-License-Identifier: MIT */
#ifndef OPENCFW_TOUCH_CLOSED_RECORD_PIPELINE_H
#define OPENCFW_TOUCH_CLOSED_RECORD_PIPELINE_H

#include <stdint.h>

/*
 * Raw little-endian buffer operations named by shipped entry address.
 * Pointer fields use the target's native pointer width. On the 32-bit G2
 * touch target the fixed pointer slots therefore reproduce the observed ABI.
 */
void open_cfw_touch_pipeline_1ac4_reset_one(
    uint32_t object_index, uint32_t record_index, const uint8_t *context);
void open_cfw_touch_pipeline_1aec_reset_object(
    uint32_t object_index, const uint8_t *context);
void open_cfw_touch_pipeline_1b1c_reset_three(const uint8_t *context);

void open_cfw_touch_pipeline_1cc2_median_shift(
    const uint8_t *unused_config, uint8_t *current, uint8_t *history);
uint32_t open_cfw_touch_pipeline_1cee_update(
    const uint8_t *config, uint8_t *record, const uint8_t *unused,
    const uint8_t *const *nested_ref);
void open_cfw_touch_pipeline_1d54_blend(
    const uint8_t *config, uint8_t *current, uint8_t *history,
    uint8_t *fraction);
void open_cfw_touch_pipeline_1da0_filter_chain(
    const uint8_t *config, uint8_t *current, uint8_t *history,
    uint8_t *fraction);

#endif
