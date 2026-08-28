/* SPDX-License-Identifier: MIT */
#include <stdint.h>

#include "runtime_touch_selection_update_pipeline.h"
#include "runtime_touch_application_state_pipeline.h"

enum { OPEN_CFW_TOUCH_RECORD_STRIDE = 10 };

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

static uint8_t *load_target_pointer(const uint8_t *source)
{
    uint32_t value = load_le32(source);
#ifdef OPEN_CFW_TOUCH_HOST_POINTER_RESOLVER
    extern uint8_t *open_cfw_touch_host_resolve_pointer(uint32_t token);
    return open_cfw_touch_host_resolve_pointer(value);
#else
    return (uint8_t *)(uintptr_t)value;
#endif
}

static uint32_t divide_u32(uint32_t numerator, uint32_t denominator)
{
    uint32_t quotient = 0u;
    uint32_t remainder = 0u;
    uint32_t bit = 32u;

    while (bit != 0u) {
        --bit;
        remainder = (remainder << 1u) | ((numerator >> bit) & 1u);
        if (remainder >= denominator) {
            remainder -= denominator;
            quotient |= 1u << bit;
        }
    }
    return quotient;
}

static int32_t divide_s32(int32_t numerator, int32_t denominator)
{
    uint32_t numerator_negative = numerator < 0;
    uint32_t denominator_negative = denominator < 0;
    uint32_t magnitude_n = numerator_negative ? 0u - (uint32_t)numerator
                                               : (uint32_t)numerator;
    uint32_t magnitude_d = denominator_negative ? 0u - (uint32_t)denominator
                                                 : (uint32_t)denominator;
    uint32_t quotient = divide_u32(magnitude_n, magnitude_d);

    return (numerator_negative != denominator_negative)
        ? (int32_t)(0u - quotient) : (int32_t)quotient;
}

void open_cfw_touch_select_15cc_peak(uint8_t *result, const uint8_t *object)
{
    uint32_t count = load_le16(&object[0x38]);
    uint32_t flags = load_le32(&object[0x30]);
    uint8_t *records;
    uint32_t peak = 0u;
    uint32_t best_index = 0xFFFFu;
    uint32_t best_sum = 0u;
    int32_t best_delta = 0;
    uint32_t index;

    if (count <= 2u) {
        count = 3u;
    }
    if ((flags & 3u) != 1u) {
        return;
    }
    records = load_target_pointer(&object[4]);
    for (index = 0u; index < count; ++index) {
        uint32_t value = load_le16(&records[index * OPEN_CFW_TOUCH_RECORD_STRIDE + 4u]);
        if (value > peak) {
            peak = value;
        }
    }
    for (index = 0u; index < count; ++index) {
        uint8_t *record = &records[index * OPEN_CFW_TOUCH_RECORD_STRIDE];
        uint32_t value = load_le16(&record[4]);
        uint32_t previous;
        uint32_t next;
        uint32_t sum;

        if (value != peak) {
            continue;
        }
        previous = index == 0u ? 0u : load_le16(&record[-6]);
        next = index >= count - 1u ? 0u : load_le16(&record[14]);
        sum = value + previous + next;
        if (sum > best_sum) {
            best_delta = (int32_t)next - (int32_t)previous;
            best_index = index;
            best_sum = sum;
        }
    }

    if (best_index == 0xFFFFu || best_sum == 0u) {
        result[4] = 0u;
        return;
    }
    {
        uint32_t base = (uint32_t)load_le16(&object[0x34]) << 8u;
        uint32_t factor;
        uint32_t offset;
        int32_t correction;
        uint32_t position;

        if ((flags & 0x100u) != 0u) {
            factor = divide_u32(base, count);
            offset = factor >> 1u;
        } else {
            factor = divide_u32(base, count - 1u);
            offset = 0u;
        }
        correction = divide_s32(
            (int32_t)((uint32_t)best_delta * factor), (int32_t)best_sum);
        position = best_index * factor + offset + (uint32_t)correction;
        result[4] = 1u;
        store_le16(load_target_pointer(result),
                   (uint16_t)((position + 0x7Fu) >> 8u));
    }
}

void open_cfw_touch_select_2794_update(uint8_t *object)
{
    uint8_t local[32] = {0};
    uint8_t *local_data = &local[8];
    uint8_t *root = load_target_pointer(object);
    uint8_t *lanes = load_target_pointer(&object[4]);
    uint8_t *counter = load_target_pointer(&object[0x28]);
    uint32_t count = load_le16(&object[0x38]);
    uint32_t position;
    uint32_t any_high = 0u;
    uint32_t index;

#ifdef OPEN_CFW_TOUCH_HOST_POINTER_RESOLVER
    extern uint32_t open_cfw_touch_host_register_temporary(uint8_t *pointer);
    {
        uint32_t token = open_cfw_touch_host_register_temporary(local_data);
        local[0] = (uint8_t)token;
        local[1] = (uint8_t)(token >> 8u);
        local[2] = (uint8_t)(token >> 16u);
        local[3] = (uint8_t)(token >> 24u);
    }
#else
    {
        uint32_t value = (uint32_t)(uintptr_t)local_data;
        local[0] = (uint8_t)value;
        local[1] = (uint8_t)(value >> 8u);
        local[2] = (uint8_t)(value >> 16u);
        local[3] = (uint8_t)(value >> 24u);
    }
#endif

    if ((root[0x23] & 1u) != 0u) {
        position = (uint32_t)load_le16(&root[8]) - load_le16(&root[0x1E]);
    } else {
        position = (uint32_t)load_le16(&root[8]) + load_le16(&root[0x1E]);
    }
    if (counter[0] != 0u) {
        --counter[0];
    }
    for (index = 0u; index < count; ++index) {
        uint8_t *lane = &lanes[index * OPEN_CFW_TOUCH_RECORD_STRIDE];
        lane[6] = load_le16(&lane[4]) > position ? 1u : 0u;
        any_high |= lane[6];
    }
    if (any_high == 0u) {
        counter[0] = root[0x20];
        root[0x23] &= (uint8_t)~1u;
    }
    if (counter[0] == 0u) {
        root[0x23] |= 1u;
        if (object[0x7B] == 2u) {
            open_cfw_touch_select_15cc_peak(local, object);
        }
        if ((load_le32(&object[0x70]) & 0xFFu) != 0u) {
            open_cfw_touch_state_172a_sync_records(local, object);
        } else {
            root[0x28] = local[4];
        }
        {
            uint8_t *destination = load_target_pointer(&root[0x24]);
            for (index = 0u; index < local[4]; ++index) {
                uint32_t byte;
                for (byte = 0u; byte < 8u; ++byte) {
                    destination[index * 8u + byte] = local_data[index * 8u + byte];
                }
            }
        }
    } else if (any_high != 0u) {
        for (index = 0u; index < count; ++index) {
            lanes[index * OPEN_CFW_TOUCH_RECORD_STRIDE + 6u] = 0u;
        }
    }
}

void open_cfw_touch_select_28a2_dispatch(uint8_t *object)
{
    uint8_t mode = object[0x7B];

    if (mode >= 2u && mode <= 3u) {
        open_cfw_touch_select_2794_update(object);
    } else if (mode == 6u) {
        open_cfw_touch_state_270a_update_lanes(object);
    }
}
