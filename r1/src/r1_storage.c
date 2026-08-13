#include "openr1/r1_storage.h"

#include <stdbool.h>

const r1_partition r1_storage_partitions[R1_STORAGE_PARTITION_COUNT] = {
    {"kv.bin",     UINT32_C(0x00000), UINT32_C(0x02000)},
    {"health.db",  UINT32_C(0x02000), UINT32_C(0x06000)},
    {"sleep.db",   UINT32_C(0x08000), UINT32_C(0x02000)},
    {"pKey.bin",   UINT32_C(0x0a000), UINT32_C(0x01000)},
    {"reserve",    UINT32_C(0x0b000), UINT32_C(0x0b000)},
    {"ep.bin",     UINT32_C(0x16000), UINT32_C(0x02000)},
    {"log.bin",    UINT32_C(0x18000), UINT32_C(0x0c000)},
};

static bool names_equal(const char *left, const char *right) {
    size_t index = 0u;
    while (left[index] != '\0' && right[index] != '\0') {
        if (left[index] != right[index]) {
            return false;
        }
        ++index;
    }
    return left[index] == right[index];
}

static void storage_write_u32(uint8_t *output, uint32_t value) {
    output[0] = (uint8_t)value;
    output[1] = (uint8_t)(value >> 8u);
    output[2] = (uint8_t)(value >> 16u);
    output[3] = (uint8_t)(value >> 24u);
}

static uint32_t storage_read_u32(const uint8_t *input) {
    return (uint32_t)input[0]
        | ((uint32_t)input[1] << 8u)
        | ((uint32_t)input[2] << 16u)
        | ((uint32_t)input[3] << 24u);
}

const r1_partition *r1_storage_partition(const char *name) {
    if (name == NULL) {
        return NULL;
    }
    for (size_t index = 0u; index < R1_STORAGE_PARTITION_COUNT; ++index) {
        if (names_equal(name, r1_storage_partitions[index].name)) {
            return &r1_storage_partitions[index];
        }
    }
    return NULL;
}

static bool range_valid(uint32_t size, uint32_t offset, size_t length) {
    return length <= UINT32_MAX && offset <= size && (uint32_t)length <= size - offset;
}

r1_error r1_flash_read(const r1_flash *flash, uint32_t offset,
                       uint8_t *output, size_t length) {
    if (flash == NULL || flash->read == NULL || (length > 0u && output == NULL)) {
        return R1_ERROR_ARGUMENT;
    }
    if (!range_valid(flash->size, offset, length)) {
        return R1_ERROR_LENGTH;
    }
    return flash->read(flash->context, offset, output, length) ? R1_OK : R1_ERROR_STATE;
}

r1_error r1_flash_program(const r1_flash *flash, uint32_t offset,
                          const uint8_t *input, size_t length) {
    if (flash == NULL || flash->program == NULL || (length > 0u && input == NULL)) {
        return R1_ERROR_ARGUMENT;
    }
    if (!range_valid(flash->size, offset, length)) {
        return R1_ERROR_LENGTH;
    }
    return flash->program(flash->context, offset, input, length) ? R1_OK : R1_ERROR_STATE;
}

r1_error r1_flash_erase(const r1_flash *flash, uint32_t offset, size_t length) {
    if (flash == NULL || flash->erase == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    if (!range_valid(flash->size, offset, length) ||
        offset % R1_FLASH_PAGE_BYTES != 0u || length % R1_FLASH_PAGE_BYTES != 0u) {
        return R1_ERROR_LENGTH;
    }
    return flash->erase(flash->context, offset, length) ? R1_OK : R1_ERROR_STATE;
}

static void memory_fill(uint8_t *bytes, uint8_t value, size_t length) {
    for (size_t index = 0u; index < length; ++index) {
        bytes[index] = value;
    }
}

void r1_memory_flash_initialize(r1_memory_flash *memory, uint8_t *bytes, uint32_t size) {
    if (memory == NULL) {
        return;
    }
    memory->bytes = bytes;
    memory->size = size;
    memory->mutations_before_failure = UINT32_MAX;
    memory->program_operations = 0u;
    memory->erase_operations = 0u;
    if (bytes != NULL) {
        memory_fill(bytes, UINT8_MAX, size);
    }
}

void r1_memory_flash_fail_after(r1_memory_flash *memory, uint32_t successful_mutations) {
    if (memory != NULL) {
        memory->mutations_before_failure = successful_mutations;
    }
}

static bool memory_read(void *context, uint32_t offset, uint8_t *output, size_t length) {
    r1_memory_flash *memory = context;
    if (memory == NULL || memory->bytes == NULL || !range_valid(memory->size, offset, length)) {
        return false;
    }
    for (size_t index = 0u; index < length; ++index) {
        output[index] = memory->bytes[offset + index];
    }
    return true;
}

static bool mutation_allowed(r1_memory_flash *memory) {
    if (memory->mutations_before_failure == 0u) {
        return false;
    }
    if (memory->mutations_before_failure != UINT32_MAX) {
        memory->mutations_before_failure -= 1u;
    }
    return true;
}

static bool memory_program(void *context, uint32_t offset,
                           const uint8_t *input, size_t length) {
    r1_memory_flash *memory = context;
    if (memory == NULL || memory->bytes == NULL || !range_valid(memory->size, offset, length)) {
        return false;
    }
    for (size_t index = 0u; index < length; ++index) {
        if (((uint8_t)~memory->bytes[offset + index] & input[index]) != 0u) {
            return false;
        }
    }
    if (!mutation_allowed(memory)) {
        return false;
    }
    for (size_t index = 0u; index < length; ++index) {
        memory->bytes[offset + index] &= input[index];
    }
    memory->program_operations += 1u;
    return true;
}

static bool memory_erase(void *context, uint32_t offset, size_t length) {
    r1_memory_flash *memory = context;
    if (memory == NULL || memory->bytes == NULL || !range_valid(memory->size, offset, length) ||
        !mutation_allowed(memory)) {
        return false;
    }
    memory_fill(memory->bytes + offset, UINT8_MAX, length);
    memory->erase_operations += 1u;
    return true;
}

r1_flash r1_memory_flash_interface(r1_memory_flash *memory) {
    const r1_flash flash = {
        memory, memory == NULL ? 0u : memory->size,
        memory_read, memory_program, memory_erase
    };
    return flash;
}

static void export_plan_chunk(r1_export_state *state, r1_export_plan *plan) {
    const uint32_t remaining = state->total_bytes - state->offset;
    const uint32_t chunk = remaining < R1_EXPORT_MAX_CHUNK_BYTES
        ? remaining : R1_EXPORT_MAX_CHUNK_BYTES;
    if (chunk == 0u) {
        plan->finalize_provider = true;
        state->active = false;
        return;
    }
    plan->send_data_marker = true;
    plan->delay_before_data_ms = R1_EXPORT_INTERFRAME_DELAY_MS;
    plan->read_offset = state->offset;
    plan->read_length = chunk;
    state->offset += chunk;
}

/* Recovered R1 generic virtual-file export policy. File composition, provider
 * callbacks, allocation, delay, and transport execution remain external. */
r1_error r1_export_plan_command(
    r1_export_state *state, const r1_export_observation *observation,
    r1_export_plan *plan) {
    if (state == NULL || observation == NULL || plan == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    *plan = (r1_export_plan){0};

    if (observation->command == 0u) {
        plan->control_length = R1_EXPORT_CONTROL_BYTES;
        if (observation->result != 1u || !observation->metadata_available) {
            plan->control[1] = 1u;
            return R1_OK;
        }
        state->total_bytes = observation->total_bytes;
        state->offset = 0u;
        state->active = true;
        plan->start_provider = true;
        plan->reset_offset = true;
        storage_write_u32(plan->control + 2u, observation->total_bytes);
        storage_write_u32(plan->control + 6u, observation->checksum);
        export_plan_chunk(state, plan);
        return R1_OK;
    }

    if (observation->command != 1u) {
        return R1_OK;
    }
    if (observation->result == 2u) {
        state->offset = 0u;
        plan->reset_offset = true;
        return R1_OK;
    }
    if (state->offset >= state->total_bytes) {
        if (state->active) {
            state->active = false;
        } else {
            plan->control[0] = 3u;
            plan->control_length = 1u;
        }
        plan->finalize_provider = true;
        return R1_OK;
    }
    export_plan_chunk(state, plan);
    return R1_OK;
}

r1_error r1_ep_scan_cursor(const uint8_t *records, size_t length,
                           r1_ep_scan_result *result) {
    if (records == NULL || result == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    if (length != R1_EP_PARTITION_BYTES) {
        return R1_ERROR_LENGTH;
    }
    *result = (r1_ep_scan_result){
        .all_records_have_magic = true,
    };
    for (size_t index = 0u; index < R1_EP_RECORD_COUNT; ++index) {
        const uint8_t *record = records + index * R1_EP_RECORD_BYTES;
        if ((record[0] & UINT8_C(0x0f)) != R1_EP_RECORD_MAGIC) {
            result->all_records_have_magic = false;
            if (!result->first_free_found) {
                result->first_free_found = true;
                result->first_free_index = (uint16_t)index;
            }
            continue;
        }
        const uint32_t timestamp = storage_read_u32(record + 4u);
        if (timestamp != 0u &&
            (!result->latest_nonzero_timestamp_found
             || timestamp >= result->latest_timestamp)) {
            result->latest_nonzero_timestamp_found = true;
            result->latest_timestamp = timestamp;
            result->latest_timestamp_index = (uint16_t)index;
        }
    }
    result->write_cursor = result->first_free_found
        ? result->first_free_index
        : (uint16_t)((result->latest_timestamp_index + 1u)
                     & (R1_EP_RECORD_COUNT - 1u));
    return R1_OK;
}
