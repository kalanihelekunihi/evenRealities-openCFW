/* SPDX-License-Identifier: MIT */
#ifndef OPENCFW_TOUCH_RECORD_PRIMITIVES_H
#define OPENCFW_TOUCH_RECORD_PRIMITIVES_H

#include <stdint.h>

/* Raw little-endian record transforms named only by shipped entry address. */
void open_cfw_touch_record_1ab8_reset(uint8_t *record);
void open_cfw_touch_record_1b36_copy_gate(
    const uint8_t *config, const uint8_t *source, uint8_t *destination,
    uint8_t *optional_gate);
void open_cfw_touch_record_1b58_replicate2(
    const uint8_t *source, uint8_t *destination);
void open_cfw_touch_record_1b60_replicate3(
    const uint8_t *source, uint8_t *destination);
void open_cfw_touch_record_1c6e_history_filter(
    const uint8_t *config, uint8_t *current, uint8_t *history);
void open_cfw_touch_record_1e88_mask3(
    uint32_t mask, uint32_t flags, uint32_t words[3]);
void open_cfw_touch_record_2620_threshold_delta(
    const uint8_t *config, uint8_t *record);

#endif
