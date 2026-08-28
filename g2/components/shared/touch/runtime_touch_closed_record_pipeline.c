/* SPDX-License-Identifier: MIT */
#include <stddef.h>
#include <stdint.h>

#include "runtime_touch_closed_record_pipeline.h"
#include "runtime_touch_leaf_primitives.h"
#include "runtime_touch_record_primitives.h"

enum {
    OPEN_CFW_TOUCH_OBJECT_STRIDE = 144,
    OPEN_CFW_TOUCH_RECORD_STRIDE = 10,
};

static uint16_t load_le16(const uint8_t *source)
{
    return (uint16_t)((uint16_t)source[0] | ((uint16_t)source[1] << 8u));
}

static void store_le16(uint8_t *destination, uint16_t value)
{
    destination[0] = (uint8_t)value;
    destination[1] = (uint8_t)(value >> 8u);
}

static uint32_t load_le32(const uint8_t *source)
{
    return (uint32_t)source[0] |
           ((uint32_t)source[1] << 8u) |
           ((uint32_t)source[2] << 16u) |
           ((uint32_t)source[3] << 24u);
}

static uint8_t *load_native_pointer(const uint8_t *source)
{
    uintptr_t value = 0u;
    size_t index;

    for (index = 0u; index < sizeof(value); ++index) {
        value |= (uintptr_t)source[index] << (index * 8u);
    }
    return (uint8_t *)value;
}

void open_cfw_touch_pipeline_1ac4_reset_one(
    uint32_t object_index, uint32_t record_index, const uint8_t *context)
{
    uint8_t *objects = load_native_pointer(&context[12]);
    uint8_t *object = &objects[object_index * OPEN_CFW_TOUCH_OBJECT_STRIDE];
    uint8_t *records = load_native_pointer(&object[4]);

    open_cfw_touch_record_1ab8_reset(
        &records[record_index * OPEN_CFW_TOUCH_RECORD_STRIDE]);
}

void open_cfw_touch_pipeline_1aec_reset_object(
    uint32_t object_index, const uint8_t *context)
{
    uint8_t *objects = load_native_pointer(&context[12]);
    uint8_t *object = &objects[object_index * OPEN_CFW_TOUCH_OBJECT_STRIDE];
    uint32_t count;

    if (object[0x7B] == 7u) {
        return;
    }
    count = load_le16(&object[0x38]);
    while (count != 0u) {
        --count;
        open_cfw_touch_pipeline_1ac4_reset_one(object_index, count, context);
    }
}

void open_cfw_touch_pipeline_1b1c_reset_three(const uint8_t *context)
{
    uint32_t object_index = 3u;

    while (object_index != 0u) {
        --object_index;
        open_cfw_touch_pipeline_1aec_reset_object(object_index, context);
    }
}

void open_cfw_touch_pipeline_1cc2_median_shift(
    const uint8_t *unused_config, uint8_t *current, uint8_t *history)
{
    uint16_t current_value = load_le16(current);
    uint16_t history0 = load_le16(history);
    uint16_t history1 = load_le16(&history[2]);
    uint32_t median;

    (void)unused_config;
    median = open_cfw_touch_leaf_1ca8_median3(
        current_value, history0, history1);
    store_le16(&history[2], history0);
    store_le16(history, current_value);
    store_le16(current, (uint16_t)median);
}

uint32_t open_cfw_touch_pipeline_1cee_update(
    const uint8_t *config, uint8_t *record, const uint8_t *unused,
    const uint8_t *const *nested_ref)
{
    uint32_t result = open_cfw_touch_leaf_1ab4_constant_0(
        (uint32_t)(uintptr_t)config, (uint32_t)(uintptr_t)record,
        (uint32_t)(uintptr_t)unused, (uint32_t)(uintptr_t)nested_ref);
    uint16_t current;
    uint16_t prior;

    if (result != 0u) {
        return result;
    }

    current = load_le16(record);
    prior = load_le16(&record[2]);
    if (current >= prior) {
        record[7] = 0u;
    }

    if ((uint32_t)prior > (uint32_t)current + load_le16(&config[0x1C])) {
        if (record[7] < load_le16(&config[0x0C])) {
            ++record[7];
        } else {
            open_cfw_touch_record_1ab8_reset(record);
        }
        return result;
    }

    if ((*nested_ref)[0x28] == 0u &&
        (uint32_t)current > (uint32_t)prior + load_le16(&config[0x1A])) {
        return result;
    }

    {
        uint32_t fixed_current = (uint32_t)current << 8u;
        uint32_t fixed_prior = ((uint32_t)prior << 8u) | record[8];
        uint32_t blended = open_cfw_touch_leaf_1cde_blend_u8(
            fixed_current, fixed_prior, config[0x22]);
        store_le16(&record[2], (uint16_t)(blended >> 8u));
        record[8] = (uint8_t)blended;
    }
    return result;
}

void open_cfw_touch_pipeline_1d54_blend(
    const uint8_t *config, uint8_t *current, uint8_t *history,
    uint8_t *fraction)
{
    uint32_t weight = load_le32(&config[0x24]);
    uint32_t blended;

    if ((load_le16(&config[0x74]) & 0x0300u) != 0x0200u) {
        blended = open_cfw_touch_leaf_1cde_blend_u8(
            load_le16(current), load_le16(history), weight);
        store_le16(history, (uint16_t)blended);
        store_le16(current, (uint16_t)blended);
        return;
    }

    blended = open_cfw_touch_leaf_1cde_blend_u8(
        (uint32_t)load_le16(current) << 8u,
        ((uint32_t)load_le16(history) << 8u) | fraction[0], weight);
    store_le16(history, (uint16_t)(blended >> 8u));
    fraction[0] = (uint8_t)blended;
    store_le16(current, (uint16_t)(blended >> 8u));
}

void open_cfw_touch_pipeline_1da0_filter_chain(
    const uint8_t *config, uint8_t *current, uint8_t *history,
    uint8_t *fraction)
{
    uint16_t flags = load_le16(&config[0x74]);

    if ((flags & 0x0010u) != 0u) {
        open_cfw_touch_pipeline_1cc2_median_shift(config, current, history);
        history += 4;
    }
    if ((flags & 0x0080u) != 0u) {
        open_cfw_touch_pipeline_1d54_blend(
            config, current, history, fraction);
        history += 2;
    }
    if ((flags & 0x0400u) != 0u) {
        open_cfw_touch_record_1c6e_history_filter(config, current, history);
    }
}
