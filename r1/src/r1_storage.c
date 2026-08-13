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

r1_error r1_latest_valid_flash_slot_scan_adapter(
    const r1_flash *flash, uint32_t base_offset, uint32_t slot_bytes,
    uint8_t slot_count, uint32_t expected_magic,
    r1_latest_valid_flash_slot_scan_result *result) {
    if (flash == NULL || result == NULL || slot_bytes == 0u) {
        return R1_ERROR_ARGUMENT;
    }
    *result = (r1_latest_valid_flash_slot_scan_result){0};
    uint8_t header[R1_FLASH_SLOT_HEADER_BYTES];
    for (uint8_t remaining = slot_count; remaining > 0u; --remaining) {
        const uint8_t slot = (uint8_t)(remaining - 1u);
        if ((uint32_t)slot > (UINT32_MAX - base_offset) / slot_bytes) {
            return R1_ERROR_LENGTH;
        }
        const uint32_t offset = base_offset + (uint32_t)slot * slot_bytes;
        ++result->read_count;
        if (r1_flash_read(flash, offset, header, sizeof header) != R1_OK) {
            result->provider_read_failed = true;
            continue;
        }
        if (storage_read_u32(header + R1_FLASH_SLOT_MAGIC_OFFSET) ==
            expected_magic) {
            result->found = true;
            result->latest_slot = slot;
            result->next_slot = (uint8_t)(slot + 1u);
            return R1_OK;
        }
    }
    return R1_OK;
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

/* Recovered R1 ep.bin readiness policy. FAL lookup, device lookup, logging,
 * synchronization creation, and the actual cursor scan remain external. */
r1_error r1_ep_plan_initialization(
    bool already_initialized, bool partition_found, bool device_found,
    uint32_t partition_bytes, r1_ep_initialization_plan *plan) {
    if (plan == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    *plan = (r1_ep_initialization_plan){0};
    if (already_initialized) {
        plan->initialized = true;
        plan->retain_partition = true;
        plan->retain_device = true;
        plan->reason = R1_EP_INITIALIZATION_READY;
        return R1_OK;
    }
    if (!partition_found) {
        plan->reason = R1_EP_INITIALIZATION_PARTITION_NOT_FOUND;
        return R1_OK;
    }
    if (!device_found) {
        plan->reason = R1_EP_INITIALIZATION_DEVICE_NOT_FOUND;
        return R1_OK;
    }
    if (partition_bytes < R1_EP_PARTITION_BYTES) {
        plan->reason = R1_EP_INITIALIZATION_PARTITION_TOO_SMALL;
        return R1_OK;
    }
    plan->initialized = true;
    plan->retain_partition = true;
    plan->retain_device = true;
    plan->scan_cursor = true;
    plan->reason = R1_EP_INITIALIZATION_READY;
    return R1_OK;
}

/* Recovered stored-sleep transport ACK callback policy. The private context,
 * event queue, marker writer, logging, and allocator remain external. */
r1_error r1_sleep_sync_plan_acknowledgement(
    bool context_present, bool event_publish_succeeded,
    r1_sleep_sync_ack_plan *plan) {
    if (plan == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    *plan = (r1_sleep_sync_ack_plan){
        .context_present = context_present,
    };
    if (!context_present) {
        return R1_OK;
    }
    plan->publish_event = true;
    plan->publish_failed = !event_publish_succeeded;
    plan->release_context = true;
    plan->event_identifier = R1_SLEEP_SYNC_MARK_EVENT;
    plan->event_payload_length = R1_SLEEP_SYNC_ACK_CONTEXT_BYTES;
    return R1_OK;
}

r1_error r1_fds_plan_event(
    uint8_t provider_event_id, uint32_t provider_result,
    uint16_t record_key, uint32_t record_id, bool metadata_validated,
    bool retry_already_pending, r1_fds_event_plan *plan) {
    if (plan == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    *plan = (r1_fds_event_plan){0};
    plan->provider_result = provider_result;
    plan->record_id = record_id;
    plan->request_next_queued_operation = retry_already_pending;

    const bool succeeded = provider_result == 0u;
    switch (provider_event_id) {
        case 1u: /* FDS_EVT_WRITE */
        case 2u: /* FDS_EVT_UPDATE */
        case 3u: /* FDS_EVT_DEL_RECORD */
            if (!metadata_validated) {
                return R1_OK;
            }
            plan->publish_event = true;
            plan->updated_record = provider_event_id == 3u;
            plan->logical_record_key = (uint16_t)(record_key + UINT16_C(0x4000));
            plan->persistence_event = succeeded
                ? R1_FDS_PERSISTENCE_RECORD_SUCCEEDED
                : R1_FDS_PERSISTENCE_RECORD_FAILED;
            break;
        case 4u: /* FDS_EVT_DEL_FILE */
            if (!metadata_validated) {
                return R1_OK;
            }
            plan->publish_event = true;
            plan->logical_record_key = (uint16_t)(record_key + UINT16_C(0x4000));
            plan->clear_file_bookkeeping = succeeded;
            plan->mark_retry_pending = true;
            plan->request_next_queued_operation = true;
            plan->persistence_event = succeeded
                ? R1_FDS_PERSISTENCE_FILE_DELETE_SUCCEEDED
                : R1_FDS_PERSISTENCE_FILE_DELETE_FAILED;
            break;
        case 5u: /* FDS_EVT_GC */
            plan->publish_event = true;
            plan->logical_record_key = UINT16_MAX;
            plan->persistence_event = succeeded
                ? R1_FDS_PERSISTENCE_GC_SUCCEEDED
                : R1_FDS_PERSISTENCE_GC_FAILED;
            break;
        default:
            break;
    }
    return R1_OK;
}
