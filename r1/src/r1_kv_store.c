#include "openr1/r1_kv_store.h"

#include "openr1/r1_crc.h"

#define R1_KV_PARTITION_MAGIC UINT32_C(0x45503130)
#define R1_KV_META_BLOCK 7u
#define R1_KV_META_PAYLOAD_BYTES 8u

typedef struct {
    uint8_t name[8];
    uint16_t length;
    uint16_t initial_flags;
} r1_kv_descriptor;

static const r1_kv_descriptor descriptors[R1_KV_CLASS_COUNT] = {
    {{'d', 'e', 'v', '_', 'i', 'n', 'f', 'o'}, 52u, 0u},
    {{'b', 'l', 'e', '_', 'm', 'u', 'l', 't'}, 90u, 0u},
    {{'h', 'e', 'a', 'l', 't', 'h', 0u, 0u}, 12u, 0u},
    {{'h', 's', 'y', 'n', 'c', 0u, 0u, 0u}, 24u, 0u},
    {{'p', 'o', 'w', 'e', 'r', 0u, 0u, 0u}, 4u, 2u},
    {{'n', 'v', '_', 'r', '1', 0u, 0u, 0u}, 124u, 2u},
    {{'r', '_', 's', 'i', 'z', 'e', 0u, 0u}, 1u, 2u},
};

static const uint8_t meta_name[8] = {'r', '1', '_', 'm', 'e', 't', 'a', 0u};

static bool valid_class(r1_kv_class class_id) {
    return (unsigned int)class_id < R1_KV_CLASS_COUNT;
}

static void copy_bytes(uint8_t *output, const uint8_t *input, size_t length) {
    for (size_t index = 0u; index < length; ++index) {
        output[index] = input[index];
    }
}

static bool equal_bytes(const uint8_t *left, const uint8_t *right, size_t length) {
    for (size_t index = 0u; index < length; ++index) {
        if (left[index] != right[index]) {
            return false;
        }
    }
    return true;
}

static uint16_t read_u16(const uint8_t *input) {
    return (uint16_t)((uint16_t)input[0] | ((uint16_t)input[1] << 8u));
}

static uint32_t read_u32(const uint8_t *input) {
    return (uint32_t)input[0] | ((uint32_t)input[1] << 8u) |
           ((uint32_t)input[2] << 16u) | ((uint32_t)input[3] << 24u);
}

static void write_u16(uint8_t *output, uint16_t value) {
    output[0] = (uint8_t)value;
    output[1] = (uint8_t)(value >> 8u);
}

static void write_u32(uint8_t *output, uint32_t value) {
    output[0] = (uint8_t)value;
    output[1] = (uint8_t)(value >> 8u);
    output[2] = (uint8_t)(value >> 16u);
    output[3] = (uint8_t)(value >> 24u);
}

static uint32_t hash131(const uint8_t name[8]) {
    uint32_t result = 0u;
    for (size_t index = 0u; index < 8u; ++index) {
        result = result * UINT32_C(0x83) + name[index];
    }
    return result;
}

static uint32_t block_offset(uint8_t slot, uint8_t block) {
    return (uint32_t)slot * R1_KV_SLOT_BYTES +
           (uint32_t)block * R1_KV_CLASS_BLOCK_BYTES;
}

static bool generation_newer(uint32_t candidate, uint32_t reference) {
    return (int32_t)(candidate - reference) > 0;
}

static void load_defaults(r1_kv_store *store) {
    for (size_t class_index = 0u; class_index < R1_KV_CLASS_COUNT; ++class_index) {
        for (size_t byte_index = 0u; byte_index < R1_KV_CLASS_PAYLOAD_MAX; ++byte_index) {
            store->payloads[class_index][byte_index] = 0u;
        }
        store->states[class_index] = 1u;
        store->flags[class_index] = descriptors[class_index].initial_flags;
        store->dirty[class_index] = false;
    }
    for (size_t index = 8u; index < 20u; ++index) {
        store->payloads[R1_KV_DEV_INFO][index] = UINT8_MAX;
    }
    store->payloads[R1_KV_DEV_INFO][20] = 'C';
    store->payloads[R1_KV_DEV_INFO][21] = 'A';
    store->payloads[R1_KV_DEV_INFO][22] = 'M';
    store->payloads[R1_KV_DEV_INFO][23] = 'H';
    store->payloads[R1_KV_DEV_INFO][24] = 1u;
    store->payloads[R1_KV_DEV_INFO][48] = 25u;

    store->payloads[R1_KV_HEALTH][0] = 20u;
    store->payloads[R1_KV_HEALTH][2] = 175u;
    store->payloads[R1_KV_HEALTH][3] = 65u;
    store->payloads[R1_KV_HEALTH][4] = 200u;
    store->payloads[R1_KV_HEALTH][6] = 50u;
    store->payloads[R1_KV_HEALTH][8] = 200u;

    for (size_t index = 0u; index < 74u; ++index) {
        store->payloads[R1_KV_NV_R1][index] = UINT8_MAX;
    }
    for (size_t index = 76u; index < 112u; ++index) {
        store->payloads[R1_KV_NV_R1][index] = UINT8_MAX;
    }
    store->payloads[R1_KV_NV_R1][112] = 0x5au;
}

static r1_error read_block(const r1_kv_store *store, uint8_t slot, uint8_t block,
                           uint8_t output[R1_KV_CLASS_BLOCK_BYTES]) {
    return r1_flash_read(&store->flash, block_offset(slot, block), output,
                         R1_KV_CLASS_BLOCK_BYTES);
}

static bool record_valid(const uint8_t block[R1_KV_CLASS_BLOCK_BYTES],
                         const uint8_t name[8], uint16_t length, uint8_t index) {
    const uint16_t flags = read_u16(block + 18u);
    return read_u32(block) == hash131(name) && equal_bytes(block + 4u, name, 8u) &&
           read_u32(block + 12u) == R1_KV_PARTITION_MAGIC &&
           (flags >> 2u) == index && read_u16(block + 20u) == length &&
           read_u16(block + 22u) == r1_crc16_modbus(block + R1_KV_CLASS_HEADER_BYTES,
                                                    length);
}

static r1_error meta_generation(const r1_kv_store *store, uint8_t slot,
                                uint32_t *generation, bool *valid) {
    uint8_t block[R1_KV_CLASS_BLOCK_BYTES];
    r1_error result = read_block(store, slot, R1_KV_META_BLOCK, block);
    if (result != R1_OK) {
        return result;
    }
    if (!record_valid(block, meta_name, R1_KV_META_PAYLOAD_BYTES, R1_KV_META_BLOCK)) {
        *valid = false;
        return R1_OK;
    }
    *generation = read_u32(block + R1_KV_CLASS_HEADER_BYTES);
    *valid = read_u32(block + R1_KV_CLASS_HEADER_BYTES + 4u) == ~*generation;
    return R1_OK;
}

static r1_error snapshot_valid(const r1_kv_store *store, uint8_t slot, bool *valid) {
    uint8_t block[R1_KV_CLASS_BLOCK_BYTES];
    for (uint8_t class_index = 0u; class_index < R1_KV_CLASS_COUNT; ++class_index) {
        r1_error result = read_block(store, slot, class_index, block);
        if (result != R1_OK) {
            return result;
        }
        if (!record_valid(block, descriptors[class_index].name,
                          descriptors[class_index].length, class_index)) {
            *valid = false;
            return R1_OK;
        }
    }
    *valid = true;
    return R1_OK;
}

static r1_error load_snapshot(r1_kv_store *store, uint8_t slot) {
    uint8_t block[R1_KV_CLASS_BLOCK_BYTES];
    for (uint8_t class_index = 0u; class_index < R1_KV_CLASS_COUNT; ++class_index) {
        r1_error result = read_block(store, slot, class_index, block);
        if (result != R1_OK) {
            return result;
        }
        store->states[class_index] = read_u16(block + 16u);
        store->flags[class_index] = (uint16_t)(read_u16(block + 18u) & 2u);
        copy_bytes(store->payloads[class_index], block + R1_KV_CLASS_HEADER_BYTES,
                   descriptors[class_index].length);
        store->dirty[class_index] = false;
    }
    return R1_OK;
}

static bool block_erased(const uint8_t block[R1_KV_CLASS_BLOCK_BYTES]) {
    for (size_t index = 0u; index < R1_KV_CLASS_BLOCK_BYTES; ++index) {
        if (block[index] != UINT8_MAX) {
            return false;
        }
    }
    return true;
}

static r1_error legacy_meta_erased(const r1_kv_store *store, uint8_t slot, bool *erased) {
    uint8_t block[R1_KV_CLASS_BLOCK_BYTES];
    r1_error result = read_block(store, slot, R1_KV_META_BLOCK, block);
    if (result != R1_OK) {
        return result;
    }
    *erased = block_erased(block);
    return R1_OK;
}

static r1_error slot_erased(const r1_kv_store *store, uint8_t slot, bool *erased) {
    uint8_t block[R1_KV_CLASS_BLOCK_BYTES];
    for (uint8_t index = 0u; index < 8u; ++index) {
        r1_error result = read_block(store, slot, index, block);
        if (result != R1_OK) {
            return result;
        }
        if (!block_erased(block)) {
            *erased = false;
            return R1_OK;
        }
    }
    *erased = true;
    return R1_OK;
}

static r1_error choose_target(r1_kv_store *store, uint8_t *target) {
    static const uint8_t initial_order[R1_KV_SLOT_COUNT] = {0u, 2u, 1u, 3u};
    if (!store->has_snapshot) {
        for (size_t index = 0u; index < R1_KV_SLOT_COUNT; ++index) {
            bool erased;
            r1_error result = slot_erased(store, initial_order[index], &erased);
            if (result != R1_OK) {
                return result;
            }
            if (erased) {
                *target = initial_order[index];
                return R1_OK;
            }
        }
        if (r1_flash_erase(&store->flash, 0u, R1_KV_SECTOR_BYTES) != R1_OK) {
            return R1_ERROR_STATE;
        }
        *target = 0u;
        return R1_OK;
    }

    const uint8_t target_sector = store->latest_slot < 2u ? 1u : 0u;
    const uint8_t first = (uint8_t)(target_sector * 2u);
    for (uint8_t slot = first; slot < (uint8_t)(first + 2u); ++slot) {
        bool erased;
        r1_error result = slot_erased(store, slot, &erased);
        if (result != R1_OK) {
            return result;
        }
        if (erased) {
            *target = slot;
            return R1_OK;
        }
    }
    if (r1_flash_erase(&store->flash,
                       (uint32_t)target_sector * R1_KV_SECTOR_BYTES,
                       R1_KV_SECTOR_BYTES) != R1_OK) {
        return R1_ERROR_STATE;
    }
    *target = first;
    return R1_OK;
}

static r1_error write_record(r1_kv_store *store, uint8_t slot, uint8_t index,
                             const uint8_t name[8], uint16_t state, uint16_t flags,
                             const uint8_t *payload, uint16_t length) {
    uint8_t block[R1_KV_CLASS_BLOCK_BYTES];
    for (size_t byte_index = 0u; byte_index < sizeof block; ++byte_index) {
        block[byte_index] = UINT8_MAX;
    }
    write_u32(block, hash131(name));
    copy_bytes(block + 4u, name, 8u);
    write_u32(block + 12u, R1_KV_PARTITION_MAGIC);
    write_u16(block + 16u, state);
    write_u16(block + 18u, (uint16_t)(((uint32_t)flags & 2u) |
                                      ((uint32_t)index << 2u)));
    write_u16(block + 20u, length);
    write_u16(block + 22u, r1_crc16_modbus(payload, length));
    copy_bytes(block + R1_KV_CLASS_HEADER_BYTES, payload, length);
    return r1_flash_program(&store->flash, block_offset(slot, index), block,
                            R1_KV_CLASS_HEADER_BYTES + length);
}

const char *r1_kv_class_name(r1_kv_class class_id) {
    static const char *const names[R1_KV_CLASS_COUNT] = {
        "dev_info", "ble_mult", "health", "hsync", "power", "nv_r1", "r_size"
    };
    return valid_class(class_id) ? names[class_id] : NULL;
}

size_t r1_kv_class_payload_length(r1_kv_class class_id) {
    return valid_class(class_id) ? descriptors[class_id].length : 0u;
}

r1_error r1_kv_store_initialize(r1_kv_store *store, r1_flash flash) {
    uint8_t selected_slot = 0u;
    uint8_t legacy_slot = 0u;
    uint32_t selected_generation = 0u;
    bool found_safe = false;
    bool found_legacy = false;

    if (store == NULL || flash.size < R1_KV_PARTITION_BYTES || flash.read == NULL ||
        flash.program == NULL || flash.erase == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    store->flash = flash;
    load_defaults(store);
    store->generation = 0u;
    store->latest_slot = 0u;
    store->has_snapshot = false;
    store->initialized = false;

    for (uint8_t slot = 0u; slot < R1_KV_SLOT_COUNT; ++slot) {
        uint32_t generation;
        bool valid;
        r1_error result = snapshot_valid(store, slot, &valid);
        if (result != R1_OK) {
            return result;
        }
        if (!valid) {
            continue;
        }
        result = meta_generation(store, slot, &generation, &valid);
        if (result != R1_OK) {
            return result;
        }
        if (valid) {
            if (!found_safe || generation_newer(generation, selected_generation)) {
                selected_slot = slot;
                selected_generation = generation;
                found_safe = true;
            }
        } else {
            result = legacy_meta_erased(store, slot, &valid);
            if (result != R1_OK) {
                return result;
            }
            if (valid) {
                legacy_slot = slot;
                found_legacy = true;
            }
        }
    }
    if (found_safe) {
        r1_error result;
        store->latest_slot = selected_slot;
        store->generation = selected_generation;
        store->has_snapshot = true;
        result = load_snapshot(store, selected_slot);
        store->initialized = result == R1_OK;
        return result;
    }
    if (found_legacy) {
        r1_error result;
        store->latest_slot = legacy_slot;
        store->has_snapshot = true;
        result = load_snapshot(store, legacy_slot);
        store->initialized = result == R1_OK;
        return result;
    }
    store->initialized = true;
    return R1_OK;
}

r1_error r1_kv_store_get(const r1_kv_store *store, r1_kv_class class_id,
                         uint8_t *output, size_t capacity, size_t *length) {
    size_t payload_length;
    if (store == NULL || !store->initialized) {
        return R1_ERROR_STATE;
    }
    if (!valid_class(class_id) || length == NULL || (output == NULL && capacity != 0u)) {
        return R1_ERROR_ARGUMENT;
    }
    payload_length = descriptors[class_id].length;
    *length = payload_length;
    if (capacity < payload_length) {
        return R1_ERROR_CAPACITY;
    }
    copy_bytes(output, store->payloads[class_id], payload_length);
    return R1_OK;
}

r1_error r1_kv_store_set(r1_kv_store *store, r1_kv_class class_id,
                         const uint8_t *payload, size_t length) {
    if (store == NULL || !store->initialized) {
        return R1_ERROR_STATE;
    }
    if (!valid_class(class_id) || payload == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    if (length != descriptors[class_id].length) {
        return R1_ERROR_LENGTH;
    }
    copy_bytes(store->payloads[class_id], payload, length);
    store->dirty[class_id] = true;
    return R1_OK;
}

r1_error r1_kv_store_commit(r1_kv_store *store) {
    uint8_t target = 0u;
    uint8_t meta_payload[R1_KV_META_PAYLOAD_BYTES];
    uint32_t generation;
    bool any_dirty = false;

    if (store == NULL || !store->initialized) {
        return R1_ERROR_STATE;
    }
    for (size_t index = 0u; index < R1_KV_CLASS_COUNT; ++index) {
        any_dirty = any_dirty || store->dirty[index];
    }
    if (!any_dirty) {
        return R1_OK;
    }
    if (choose_target(store, &target) != R1_OK) {
        return R1_ERROR_STATE;
    }
    generation = store->generation + 1u;
    write_u32(meta_payload, generation);
    write_u32(meta_payload + 4u, ~generation);

    for (uint8_t index = 1u; index < R1_KV_CLASS_COUNT; ++index) {
        if (write_record(store, target, index, descriptors[index].name,
                         store->states[index], store->flags[index],
                         store->payloads[index], descriptors[index].length) != R1_OK) {
            return R1_ERROR_STATE;
        }
    }
    if (write_record(store, target, R1_KV_META_BLOCK, meta_name, 1u, 0u,
                     meta_payload, R1_KV_META_PAYLOAD_BYTES) != R1_OK) {
        return R1_ERROR_STATE;
    }
    if (write_record(store, target, 0u, descriptors[0].name, store->states[0],
                     store->flags[0], store->payloads[0], descriptors[0].length) != R1_OK) {
        return R1_ERROR_STATE;
    }
    store->generation = generation;
    store->latest_slot = target;
    store->has_snapshot = true;
    for (size_t index = 0u; index < R1_KV_CLASS_COUNT; ++index) {
        store->dirty[index] = false;
    }
    return R1_OK;
}
