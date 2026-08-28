/* SPDX-License-Identifier: MIT */
#include <stddef.h>
#include <stdint.h>

#include "runtime_touch_application_state_pipeline.h"
#include "runtime_touch_leaf_primitives.h"

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

static void store_le32(uint8_t *destination, uint32_t value)
{
    destination[0] = (uint8_t)value;
    destination[1] = (uint8_t)(value >> 8u);
    destination[2] = (uint8_t)(value >> 16u);
    destination[3] = (uint8_t)(value >> 24u);
}

static uint8_t *load_native_pointer(const uint8_t *source)
{
    uint32_t value = load_le32(source);
#ifdef OPEN_CFW_TOUCH_HOST_POINTER_RESOLVER
    extern uint8_t *open_cfw_touch_host_resolve_pointer(uint32_t token);
    return open_cfw_touch_host_resolve_pointer(value);
#else
    return (uint8_t *)(uintptr_t)value;
#endif
}

static uint8_t *object_at(const uint8_t *context, uint32_t object_index)
{
    uint8_t *objects = load_native_pointer(&context[12]);
    return &objects[object_index * OPEN_CFW_TOUCH_OBJECT_STRIDE];
}

uint32_t open_cfw_touch_state_1ebc_pack(
    const uint8_t *selector, uint8_t *output, const uint8_t *context)
{
    uint32_t object_index = load_le16(selector);
    uint32_t record_index = load_le16(&selector[2]);
    uint8_t *object = object_at(context, object_index);
    uint8_t *root = load_native_pointer(object);
    uint8_t *auxiliary = load_native_pointer(&context[8]);
    uint8_t *descriptors = load_native_pointer(&context[16]);
    uint8_t *descriptor = &descriptors[object_index * 60u];
    uint16_t count = load_le16(&descriptor[0x36]);
    uint8_t mode = object[0x7A];
    uint32_t packed = 0x00400000u;

    if (count != 0u) {
        --count;
    }
    store_le32(&output[12], load_le32(&output[12]) |
               (((uint32_t)count << 16u) & 0x0FFF0000u));

    if ((mode == 1u && auxiliary[0x5A] == 1u) ||
        (mode == 2u && auxiliary[0x5B] == 1u) ||
        (mode == 10u && auxiliary[0x5C] == 1u)) {
        packed = 0x00C00000u |
                 (((uint32_t)root[0x33] << 28u) & 0x70000000u);
    }

    if ((load_le32(&load_native_pointer(&context[4])[8]) & 0x1000u) == 0u) {
        uint8_t first = root[0x2E];
        uint8_t second = root[0x30];

        if (mode == 1u && object[0x3A] <= record_index) {
            first = root[0x2F];
            second = root[0x31];
        }
        packed |= first;
        packed |= ((uint32_t)second << 16u) & 0x001F0000u;
        if (mode == 1u) {
            uint8_t *records = load_native_pointer(&object[4]);
            packed |= (uint32_t)records[record_index * OPEN_CFW_TOUCH_RECORD_STRIDE + 9u]
                      << 8u;
        }
    }
    store_le32(&output[16], packed);
    return 0u;
}

void open_cfw_touch_state_16d4_copy8(
    uint32_t flags, const uint8_t *source, uint8_t *destination)
{
    size_t index;

    if ((flags & 2u) == 0u) {
        return;
    }
    for (index = 0u; index < 8u; ++index) {
        destination[index] = source[index];
    }
}

void open_cfw_touch_state_16e6_blend_pair(
    const uint8_t *config, uint8_t *current, uint8_t *history)
{
    uint32_t flags = load_le32(&config[0x70]);
    uint32_t weight;
    uint16_t first;
    uint16_t second;

    if ((flags & 2u) == 0u) {
        return;
    }
    weight = (flags >> 16u) & 0xFFu;
    first = (uint16_t)open_cfw_touch_leaf_1cde_blend_u8(
        load_le16(current), load_le16(history), weight);
    store_le16(history, first);
    second = (uint16_t)open_cfw_touch_leaf_1cde_blend_u8(
        load_le16(&current[2]), load_le16(&history[2]), weight);
    store_le16(&history[2], second);
    store_le16(current, first);
    store_le16(&current[2], second);
}

void open_cfw_touch_state_172a_sync_records(
    const uint8_t *control, uint8_t *object)
{
    uint32_t count = control[4];
    uint8_t *group = load_native_pointer(&object[0x3C]);
    uint32_t index;

    if (count != 0u && count != 0xFFu) {
        uint32_t flags = load_le32(&object[0x70]);
        uint32_t stride = (flags >> 8u) & 0xFFu;
        uint32_t previous = group[4];
        uint8_t *source = load_native_pointer(control);
        uint8_t *destination = load_native_pointer(group);

        if (previous == 0xFFu) {
            previous = 0u;
        } else if (previous > count) {
            previous = count;
        }
        for (index = 0u; index < previous; ++index) {
            open_cfw_touch_state_16e6_blend_pair(
                object, source, destination);
            source += 8u;
            destination += stride * 8u;
        }
        for (; index < count; ++index) {
            open_cfw_touch_state_16d4_copy8(flags, source, destination);
            source += 8u;
            destination += stride * 8u;
        }
    }
    group[4] = (uint8_t)count;
}

void open_cfw_touch_state_2568_reset_object(
    uint32_t object_index, const uint8_t *context)
{
    uint8_t *object = object_at(context, object_index);
    uint8_t *root = load_native_pointer(object);
    uint8_t *records = load_native_pointer(&object[4]);
    uint32_t count = load_le16(&object[0x38]);
    uint8_t mode = object[0x7B];
    uint32_t index;

    if (mode == 7u) {
        return;
    }
    root[0x23] &= (uint8_t)~1u;
    for (index = 0u; index < count; ++index) {
        records[index * OPEN_CFW_TOUCH_RECORD_STRIDE + 6u] &= (uint8_t)~3u;
    }
    if (mode == 6u) {
        uint8_t *destination = load_native_pointer(&object[0x28]);
        for (index = 0u; index < count * 2u; ++index) {
            destination[index] = root[0x20];
        }
    }
    if (mode >= 2u && mode <= 5u) {
        root[0x28] = 0u;
        if ((load_le32(&object[0x70]) & 0xFFu) != 0u) {
            load_native_pointer(&object[0x3C])[4] = 0u;
        }
        if (mode != 4u && object[0x7A] == 1u) {
            load_native_pointer(&object[0x28])[0] = root[0x20];
        }
    }
}

void open_cfw_touch_state_270a_update_lanes(uint8_t *context)
{
    uint8_t *root = load_native_pointer(context);
    uint8_t *lane = load_native_pointer(&context[4]);
    uint8_t *counter = load_native_pointer(&context[0x28]);
    uint32_t lane_count = (uint32_t)load_le16(&context[0x38]) * 2u;
    uint32_t index;

    root[0x23] &= (uint8_t)~1u;
    for (index = 0u; index < lane_count; ++index) {
        uint8_t mask = (index & 1u) != 0u ? 2u : 1u;
        uint32_t value = load_le16(&root[(index & 1u) != 0u ? 0x0A : 0x08]);
        uint32_t delta = load_le16(&root[0x1E]);

        if ((lane[6] & mask) != 0u) {
            value -= delta;
        } else {
            value += delta;
        }
        if (counter[0] != 0u) {
            --counter[0];
        }
        if (load_le16(&lane[4]) <= value) {
            counter[0] = root[0x20];
            lane[6] &= (uint8_t)~mask;
        }
        if (counter[0] == 0u) {
            lane[6] |= mask;
        }
        if ((lane[6] & mask) != 0u) {
            root[0x23] |= 1u;
        }
        ++counter;
        if ((index & 1u) != 0u) {
            lane += OPEN_CFW_TOUCH_RECORD_STRIDE;
        }
    }
}

void open_cfw_touch_state_28c0_cap_object(
    uint32_t object_index, const uint8_t *context)
{
    uint8_t *object = object_at(context, object_index);
    uint8_t *root = load_native_pointer(object);
    uint8_t *records = load_native_pointer(&object[4]);
    uint32_t count = load_le16(&object[0x38]);
    uint16_t first_limit = load_le16(&root[4]);
    uint32_t index;

    for (index = 0u; index < count; ++index) {
        uint16_t limit = first_limit;
        uint16_t value;

        if (object[0x7A] == 1u && object[0x3A] <= index) {
            limit = load_le16(&root[6]);
        }
        value = load_le16(&records[index * OPEN_CFW_TOUCH_RECORD_STRIDE]);
        if (value > limit) {
            store_le16(&records[index * OPEN_CFW_TOUCH_RECORD_STRIDE], limit);
        }
    }
}

void open_cfw_touch_state_2902_cap_enabled_object(
    uint32_t object_index, const uint8_t *context)
{
    if (object_at(context, object_index)[0x7B] != 7u) {
        open_cfw_touch_state_28c0_cap_object(object_index, context);
    }
}

void open_cfw_touch_state_291e_cap_record(
    uint32_t object_index, uint32_t record_index, const uint8_t *context)
{
    uint8_t *object = object_at(context, object_index);
    uint8_t *root = load_native_pointer(object);
    uint8_t *records = load_native_pointer(&object[4]);
    uint16_t limit = load_le16(&root[4]);
    uint8_t *record = &records[record_index * OPEN_CFW_TOUCH_RECORD_STRIDE];
    uint16_t value;

    if (object[0x7A] == 1u && object[0x3A] <= record_index) {
        limit = load_le16(&root[6]);
    }
    value = load_le16(record);
    if (value > limit) {
        store_le16(record, limit);
    }
}

void open_cfw_touch_state_2956_cap_enabled_record(
    uint32_t object_index, uint32_t record_index, const uint8_t *context)
{
    if (object_at(context, object_index)[0x7B] != 7u) {
        open_cfw_touch_state_291e_cap_record(
            object_index, record_index, context);
    }
}

uint32_t open_cfw_touch_state_298e_status80(const uint8_t *context)
{
    uint8_t *nested = load_native_pointer(&context[4]);
    return load_le32(&nested[8]) & 0x80u;
}
