/* SPDX-License-Identifier: MIT */
#include <stddef.h>
#include <stdint.h>

#include "runtime_touch_configuration_start_pipeline.h"

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

uint32_t open_cfw_touch_config_1944_start(
    uint8_t *object, const open_cfw_touch_configuration_providers *providers)
{
    uint8_t *root;
    uint8_t *capture_context;
    uint8_t *busy;
    uint32_t status;

    if (object == NULL || providers == NULL || providers->capture == NULL ||
            providers->event == NULL) {
        return 0x80u;
    }
    root = load_target_pointer(object);
    capture_context = load_target_pointer(&root[8]);
    busy = load_target_pointer(&capture_context[4]);
    if (busy[0] != 0u) {
        return 0x80u;
    }
    status = providers->capture(load_le32(capture_context), 2u);
    if (status != 0u) {
        return 8u;
    }
    return providers->event(1u, object);
}

uint32_t open_cfw_touch_config_1972_start_wrapper(
    uint8_t *object, const open_cfw_touch_configuration_providers *providers)
{
    return open_cfw_touch_config_1944_start(object, providers);
}

uint32_t open_cfw_touch_config_197c_initialize(
    uint8_t *object, const open_cfw_touch_configuration_providers *providers)
{
    uint8_t *root;
    uint8_t *state;
    uint8_t *record_holder;
    uint8_t *record;
    uint32_t index;
    uint32_t status;

    if (object == NULL || providers == NULL || providers->event == NULL) {
        return 1u;
    }
    root = load_target_pointer(object);
    state = load_target_pointer(&object[8]);
    record_holder = load_target_pointer(&object[0x0C]);
    record = load_target_pointer(record_holder);

    state[0x74] = 0u;
    state[0x75] = 0u;
    store_le32(&state[0x00], 0u);
    store_le32(&state[0x04], 0u);
    store_le32(&state[0x08], 0u);
    store_le32(&state[0x0C], 0u);
    for (index = 0u; index < 3u; ++index) {
        record[index * 0x3Cu + 0x23u] |= 6u;
    }
    store_le32(&state[0x1C], 0u);
    store_le32(&state[0x2C], 0x0000028Fu);
    store_le32(&state[0x14], 0u);
    state[0x4C] = 0u;
    state[0x57] = root[0x2F];
    state[0x58] = root[0x2D];
    state[0x59] = root[0x31];
    store_le16(&state[0x30], load_le16(&root[0x16]));
    store_le16(&state[0x32], load_le16(&root[0x18]));
    state[0x53] = root[0x34];
    state[0x54] = root[0x35];
    store_le16(&state[0x3C], 0x084Cu);
    state[0x4E] = 0u;
    state[0x4F] = 0xFFu;
    state[0x50] = 0x8Eu;
    state[0x51] = 1u;
    for (index = 0u; index < 3u; ++index) {
        uint8_t *item = &record[index * 0x3Cu];
        if (load_le16(&item[4]) == 0u) {
            item[0x23] |= 8u;
        }
        if (load_le16(&item[6]) == 0u) {
            item[0x23] |= 0x10u;
        }
    }
    store_le16(&state[0x40], load_le16(&root[0x1E]));
    store_le16(&state[0x3E], load_le16(&root[0x1C]));
    store_le16(&state[0x44], load_le16(&root[0x22]));
    store_le16(&state[0x42], load_le16(&root[0x20]));
    state[0x72] = 3u;
    state[0x4D] = 3u;
    state[0x5A] = 3u;
    state[0x5B] = 0u;
    state[0x5C] = 0u;
    state[0x5D] = 6u;
    state[0x5E] = 4u;
    state[0x5F] = 10u;
    state[0x60] = 3u;
    store_le32(&state[0x24], 0x0000F424u);
    store_le16(&state[0x4A], 0x0020u);

    status = providers->event(0u, object);
    if (status != 0u) {
        return status;
    }
    return open_cfw_touch_config_1972_start_wrapper(object, providers);
}
