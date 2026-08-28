/* SPDX-License-Identifier: MIT */
#include <stddef.h>
#include "runtime_touch_record_primitives.h"

static uint16_t load_le16(const uint8_t *source)
{
    return (uint16_t)((uint16_t)source[0] | ((uint16_t)source[1] << 8u));
}

static void store_le16(uint8_t *destination, uint16_t value)
{
    destination[0] = (uint8_t)value;
    destination[1] = (uint8_t)(value >> 8u);
}

void open_cfw_touch_record_1ab8_reset(uint8_t *record)
{
    uint16_t first = load_le16(record);
    record[8] = 0u;
    store_le16(&record[2], first);
    record[7] = 0u;
}

void open_cfw_touch_record_1b36_copy_gate(
    const uint8_t *config, const uint8_t *source, uint8_t *destination,
    uint8_t *optional_gate)
{
    store_le16(destination, load_le16(source));
    if (optional_gate != NULL && (load_le16(&config[0x74]) & 0x0300u) == 0x0200u) {
        optional_gate[0] = 0u;
    }
}

void open_cfw_touch_record_1b58_replicate2(
    const uint8_t *source, uint8_t *destination)
{
    uint16_t value = load_le16(source);
    store_le16(destination, value);
    store_le16(&destination[2], value);
}

void open_cfw_touch_record_1b60_replicate3(
    const uint8_t *source, uint8_t *destination)
{
    uint16_t value = load_le16(source);
    store_le16(destination, value);
    store_le16(&destination[2], value);
    store_le16(&destination[4], load_le16(source));
}

void open_cfw_touch_record_1c6e_history_filter(
    const uint8_t *config, uint8_t *current, uint8_t *history)
{
    uint16_t current_value = load_le16(current);
    uint16_t history0 = load_le16(history);
    uint32_t sum = (uint32_t)current_value + history0;

    if ((load_le16(&config[0x74]) & 0x1800u) == 0x1000u) {
        uint16_t history1 = load_le16(&history[2]);
        uint16_t history2 = load_le16(&history[4]);
        sum += (uint32_t)history1 + history2;
        store_le16(&history[4], history1);
        store_le16(&history[2], history0);
        store_le16(history, current_value);
        store_le16(current, (uint16_t)(sum >> 2u));
    } else {
        store_le16(history, current_value);
        store_le16(current, (uint16_t)(sum >> 1u));
    }
}

void open_cfw_touch_record_1e88_mask3(
    uint32_t mask, uint32_t flags, uint32_t words[3])
{
    uint32_t original0 = words[0];
    uint32_t original1 = words[1];
    uint32_t original2 = words[2];
    words[0] = (original0 & ~mask) | ((flags & 4u) != 0u ? mask : 0u);
    words[1] = (original1 & ~mask) | ((flags & 2u) != 0u ? mask : 0u);
    words[2] = (original2 & ~mask) | ((flags & 1u) != 0u ? mask : 0u);
}

void open_cfw_touch_record_2620_threshold_delta(
    const uint8_t *config, uint8_t *record)
{
    uint16_t value0 = load_le16(record);
    uint16_t value1 = load_le16(&record[2]);
    uint16_t threshold = load_le16(&config[0x1A]);
    store_le16(&record[4], 0u);
    if ((uint32_t)value0 > (uint32_t)value1 + threshold) {
        store_le16(&record[4], (uint16_t)(value0 - value1));
    }
}
