/* SPDX-License-Identifier: MIT */
#include <stdint.h>

#include "runtime_touch_application_packet_pipeline.h"
#include "runtime_touch_application_state_pipeline.h"
#include "runtime_touch_leaf_primitives.h"
#include "runtime_touch_record_primitives.h"

enum {
    OPEN_CFW_TOUCH_OBJECT_STRIDE = 144,
    OPEN_CFW_TOUCH_DESCRIPTOR_STRIDE = 60,
};

static uint16_t load_le16(const uint8_t *source)
{
    return (uint16_t)((uint16_t)source[0] | ((uint16_t)source[1] << 8u));
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

static uint8_t *object_at(const uint8_t *context, uint32_t object_index)
{
    return &load_target_pointer(&context[12])[
        object_index * OPEN_CFW_TOUCH_OBJECT_STRIDE];
}

static uint8_t *descriptor_at(const uint8_t *context, uint32_t object_index)
{
    return &load_target_pointer(&context[16])[
        object_index * OPEN_CFW_TOUCH_DESCRIPTOR_STRIDE];
}

static uint32_t list_mask(const uint8_t *list, uint32_t count)
{
    uint32_t mask = 0u;
    uint32_t index;

    for (index = 0u; index < count; ++index) {
        mask |= 1u << list[index * 8u + 5u];
    }
    return mask;
}

uint32_t open_cfw_touch_packet_2248_build_entry(
    uint32_t group, uint32_t item_index, uint8_t *output,
    const uint8_t *context)
{
    uint8_t *mapping = load_target_pointer(
        &context[group == 0u ? 0x30 : 0x34]) + item_index * 4u;
    uint32_t object_index = load_le16(mapping);
    uint8_t *object = object_at(context, object_index);
    uint8_t *descriptor = descriptor_at(context, object_index);
    uint8_t *global = load_target_pointer(&context[8]);
    uint8_t mode = object[0x7A];
    uint8_t *packed_output = output;
    uint32_t result;

    if (group == 1u) {
        uint32_t word0 = global[0x60] & 0x0Fu;
        uint32_t word8;

        word0 |= ((uint32_t)global[0x5D] << 4u) & 0xF0u;
        word0 |= ((uint32_t)global[0x5E] << 8u) & 0x0F00u;
        word0 |= ((uint32_t)load_le16(&descriptor[0x0C]) << 16u) & 0x003F0000u;
        word0 |= (uint32_t)global[0x5F] << 24u;
        store_le32(output, word0);
        store_le32(&output[4],
                   load_le16(&descriptor[0x1A]) |
                   ((uint32_t)load_le16(&descriptor[0x1C]) << 16u));
        word8 = load_le16(&descriptor[8]);
        word8 |= ((uint32_t)descriptor[0x20] << 16u) & 0x00070000u;
        if (mode != 1u) {
            word8 |= 0x01000000u;
        }
        store_le32(&output[8], word8);
        store_le32(&output[12], 0u);
        store_le32(&output[16], 0u);
        packed_output += 20u;
    }

    store_le32(&packed_output[0x18], (uint32_t)object[0x8C] << 24u);
    store_le32(&packed_output[0x0C],
               ((((uint32_t)object[0x84] - 1u) << 14u) & 0x00004000u) |
               (((uint32_t)load_le16(&descriptor[0x2C]) - 1u) & 0x0003FFFFu));
    if (descriptor[0x34] == 1u && load_le16(&object[0x80]) != item_index) {
        store_le32(&packed_output[0x0C],
                   load_le32(&packed_output[0x0C]) | 0x00008000u);
    }

    result = open_cfw_touch_state_1ebc_pack(mapping, packed_output, context);
    if (result != 0u) {
        return result;
    }
    if (mode != 1u) {
        return 1u;
    }

    {
        uint32_t scale = descriptor[0x20];
        uint32_t value = open_cfw_touch_leaf_2228_mode_scale(
            mode, scale, load_le16(&descriptor[0x0E]));
        uint32_t word = ((value - 1u) << 16u) & 0x0FFF0000u;
        word |= (scale << 28u) & 0x30000000u;
        word |= (uint32_t)descriptor[0x38] << 30u;
        word |= 3u;
        store_le32(&packed_output[0x14], word);
    }
    return 0u;
}

void open_cfw_touch_packet_23a4_build_group(
    uint32_t group, uint8_t *context)
{
    uint8_t *root = load_target_pointer(context);
    uint8_t *global = load_target_pointer(&context[8]);
    uint8_t *first_list = load_target_pointer(&context[0x14]);
    uint8_t *second_list = load_target_pointer(&context[0x18]);
    uint32_t available = list_mask(first_list, load_le16(&root[0x0C]));
    uint32_t second_count = root[0x2C];
    uint32_t threshold_a;
    uint32_t threshold_base = global[0x64];
    uint32_t choice;
    uint8_t *output;
    uint8_t *mapping;
    uint32_t item_count;
    uint32_t item_index;

    available |= list_mask(second_list, second_count);
    if (global[0x75] == 2u) {
        threshold_a = global[0x64];
    } else if (global[0x75] == 5u) {
        threshold_a = global[0x6D];
    } else {
        threshold_a = global[0x63];
    }
    if (global[0x74] == 2u) {
        choice = threshold_base;
    } else if (global[0x74] == 4u) {
        choice = global[0x6B];
    } else {
        choice = global[0x63];
    }

    if (group == 1u) {
        output = load_target_pointer(&context[0x2C]);
        mapping = load_target_pointer(&context[0x34]);
        item_count = 4u;
    } else {
        output = load_target_pointer(&context[0x28]);
        mapping = load_target_pointer(&context[0x30]);
        item_count = 5u;
    }

    for (item_index = 0u; item_index < item_count; ++item_index) {
        uint8_t *entry_mapping = &mapping[item_index * 4u];
        uint32_t object_index;
        uint32_t sub_index;
        uint8_t *object;
        uint8_t mode;
        uint32_t flags;
        uint8_t *words;

        (void)open_cfw_touch_packet_2248_build_entry(
            group, item_index, output, context);
        object_index = load_le16(entry_mapping);
        sub_index = load_le16(&entry_mapping[2]);
        object = object_at(context, object_index);
        mode = object[0x7A];
        flags = mode == 1u ? choice : (mode == 2u ? threshold_a : threshold_base);
        words = group == 1u ? &output[20] : output;
        open_cfw_touch_record_1e88_mask3(
            available, flags, (uint32_t *)(void *)words);

        if (second_count != 0u) {
            uint32_t repeat_count = mode == 1u ? global[0x6B] : second_count;
            uint32_t mask = list_mask(second_list, repeat_count);
            open_cfw_touch_record_1e88_mask3(
                mask, flags, (uint32_t *)(void *)words);
        }
        if (mode == 1u) {
            uint8_t *descriptor = load_target_pointer(&object[8]) + sub_index * 8u;
            uint8_t *child_list = load_target_pointer(descriptor);
            uint32_t mask = list_mask(child_list, descriptor[5]);
            open_cfw_touch_record_1e88_mask3(
                mask, global[0x68], (uint32_t *)(void *)words);
        }

        output = group == 1u ? &words[24] : &output[28];
    }
}
