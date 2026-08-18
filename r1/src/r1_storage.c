#include "openr1/r1_storage.h"

#include "openr1/r1_crc.h"

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
    memory->bytes_before_failure = UINT32_MAX;
    memory->program_operations = 0u;
    memory->erase_operations = 0u;
    memory->byte_mutations = 0u;
    memory->byte_failure_enabled = false;
    if (bytes != NULL) {
        memory_fill(bytes, UINT8_MAX, size);
    }
}

void r1_memory_flash_fail_after(r1_memory_flash *memory, uint32_t successful_mutations) {
    if (memory != NULL) {
        memory->mutations_before_failure = successful_mutations;
        memory->bytes_before_failure = UINT32_MAX;
        memory->byte_failure_enabled = false;
    }
}

void r1_memory_flash_fail_after_bytes(
    r1_memory_flash *memory, uint32_t successful_bytes) {
    if (memory != NULL) {
        memory->mutations_before_failure = UINT32_MAX;
        memory->bytes_before_failure = successful_bytes;
        memory->byte_failure_enabled = successful_bytes != UINT32_MAX;
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

static bool byte_mutation_allowed(r1_memory_flash *memory) {
    if (!memory->byte_failure_enabled) {
        return true;
    }
    if (memory->bytes_before_failure == 0u) {
        return false;
    }
    memory->bytes_before_failure -= 1u;
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
        if (!byte_mutation_allowed(memory)) {
            return false;
        }
        memory->bytes[offset + index] &= input[index];
        memory->byte_mutations += 1u;
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
    for (size_t index = 0u; index < length; ++index) {
        if (!byte_mutation_allowed(memory)) {
            return false;
        }
        memory->bytes[offset + index] = UINT8_MAX;
        memory->byte_mutations += 1u;
    }
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

static void ep_scan_begin(r1_ep_scan_result *result) {
    *result = (r1_ep_scan_result){
        .all_records_have_magic = true,
    };
}

static void ep_scan_record(
    r1_ep_scan_result *result, const uint8_t record[R1_EP_RECORD_BYTES],
    size_t index) {
    if ((record[0] & UINT8_C(0x0f)) != R1_EP_RECORD_MAGIC) {
        result->all_records_have_magic = false;
        if (!result->first_free_found) {
            result->first_free_found = true;
            result->first_free_index = (uint16_t)index;
        }
        return;
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

static void ep_scan_finish(r1_ep_scan_result *result) {
    result->write_cursor = result->first_free_found
        ? result->first_free_index
        : (uint16_t)((result->latest_timestamp_index + 1u)
                     & (R1_EP_RECORD_COUNT - 1u));
}

r1_error r1_ep_scan_cursor(const uint8_t *records, size_t length,
                           r1_ep_scan_result *result) {
    if (records == NULL || result == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    if (length != R1_EP_PARTITION_BYTES) {
        return R1_ERROR_LENGTH;
    }
    ep_scan_begin(result);
    for (size_t index = 0u; index < R1_EP_RECORD_COUNT; ++index) {
        const uint8_t *record = records + index * R1_EP_RECORD_BYTES;
        ep_scan_record(result, record, index);
    }
    ep_scan_finish(result);
    return R1_OK;
}

r1_error r1_ep_scan_flash_cursor(
    const r1_flash *flash, uint32_t partition_offset,
    r1_ep_scan_result *result) {
    if (flash == NULL || result == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    if (partition_offset > flash->size ||
        R1_EP_PARTITION_BYTES > flash->size - partition_offset) {
        return R1_ERROR_LENGTH;
    }
    ep_scan_begin(result);
    uint8_t record[R1_EP_RECORD_BYTES];
    for (size_t index = 0u; index < R1_EP_RECORD_COUNT; ++index) {
        const uint32_t offset = partition_offset +
            (uint32_t)(index * R1_EP_RECORD_BYTES);
        const r1_error error = r1_flash_read(
            flash, offset, record, sizeof(record));
        if (error != R1_OK) {
            return error;
        }
        ep_scan_record(result, record, index);
    }
    ep_scan_finish(result);
    return R1_OK;
}

static uint32_t log_bin_sector_offset(
    const r1_log_bin_store *store, uint16_t sector) {
    return store->partition_offset +
        (uint32_t)sector * R1_LOG_BIN_SECTOR_BYTES;
}

static r1_error log_bin_page_erased(
    const r1_log_bin_store *store, uint16_t sector, bool *erased) {
    if (erased == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    uint8_t probe[4];
    const r1_error error = r1_flash_read(
        store->flash,
        log_bin_sector_offset(store, sector) +
            R1_LOG_BIN_ERASED_PROBE_OFFSET,
        probe, sizeof(probe));
    if (error != R1_OK) {
        return error;
    }
    *erased = probe[0] == UINT8_MAX && probe[1] == UINT8_MAX &&
        probe[2] == UINT8_MAX && probe[3] == UINT8_MAX;
    return R1_OK;
}

static r1_error log_bin_erase_if_needed(
    r1_log_bin_store *store, uint16_t sector) {
    bool erased = false;
    r1_error error = log_bin_page_erased(store, sector, &erased);
    if (error != R1_OK || erased) {
        return error;
    }
    return r1_flash_erase(
        store->flash, log_bin_sector_offset(store, sector),
        R1_LOG_BIN_SECTOR_BYTES);
}

r1_error r1_log_bin_bind(
    r1_log_bin_store *store, const r1_flash *flash,
    uint32_t partition_offset, uint32_t partition_bytes) {
    if (store == NULL || flash == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    *store = (r1_log_bin_store){0};
    if (partition_bytes != R1_LOG_BIN_PARTITION_BYTES ||
        partition_offset > flash->size ||
        partition_bytes > flash->size - partition_offset) {
        return R1_ERROR_LENGTH;
    }
    *store = (r1_log_bin_store){
        .flash = flash,
        .partition_offset = partition_offset,
        .bound = true,
    };
    return R1_OK;
}

uint16_t r1_log_bin_sector_count(const r1_log_bin_store *store) {
    return store != NULL && store->bound ? R1_LOG_BIN_SECTOR_COUNT : 0u;
}

r1_error r1_log_bin_initialize(r1_log_bin_store *store) {
    if (store == NULL || !store->bound || store->flash == NULL) {
        return R1_ERROR_STATE;
    }
    store->current_sector = 0u;
    store->sector_offset = 0u;
    for (uint16_t sector = 0u;
         sector < R1_LOG_BIN_SECTOR_COUNT; ++sector) {
        bool erased = false;
        const r1_error error = log_bin_page_erased(store, sector, &erased);
        if (error != R1_OK) {
            return error;
        }
        if (erased) {
            store->current_sector = sector;
            store->initialized = true;
            return R1_OK;
        }
    }
    /* Recovered full-partition fallback. The first write erases sector zero
     * through the same selected-page check used after page advances. */
    store->initialized = true;
    return R1_OK;
}

r1_error r1_log_bin_write(
    r1_log_bin_store *store, const uint8_t *input, size_t length) {
    if (store == NULL || input == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    if (length == 0u || length > R1_LOG_BIN_MAX_WRITE_BYTES) {
        return R1_ERROR_LENGTH;
    }
    if (!store->initialized) {
        const r1_error error = r1_log_bin_initialize(store);
        if (error != R1_OK) {
            return error;
        }
    }
    if (length > R1_LOG_BIN_SECTOR_BYTES - store->sector_offset) {
        store->current_sector = (uint16_t)(
            (store->current_sector + 1u) % R1_LOG_BIN_SECTOR_COUNT);
        store->sector_offset = 0u;
    }
    if (store->sector_offset == 0u) {
        const r1_error erase_error = log_bin_erase_if_needed(
            store, store->current_sector);
        if (erase_error != R1_OK) {
            return erase_error;
        }
    }
    const r1_error write_error = r1_flash_program(
        store->flash,
        log_bin_sector_offset(store, store->current_sector) +
            store->sector_offset,
        input, length);
    if (write_error != R1_OK) {
        return write_error;
    }
    store->sector_offset = (uint16_t)(store->sector_offset + length);
    const uint16_t next_sector = (uint16_t)(
        (store->current_sector + 1u) % R1_LOG_BIN_SECTOR_COUNT);
    return log_bin_erase_if_needed(store, next_sector);
}

static bool structured_log_ready(const r1_structured_log_cache *cache) {
    return cache != NULL && cache->initialized && cache->bytes != NULL &&
        cache->capacity >= 3u && cache->read_index < cache->capacity &&
        cache->write_index < cache->capacity;
}

r1_error r1_structured_log_cache_initialize(
    r1_structured_log_cache *cache, uint8_t *bytes, size_t capacity) {
    if (cache == NULL || bytes == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    *cache = (r1_structured_log_cache){0};
    if (capacity < 3u || capacity > UINT32_MAX) {
        return R1_ERROR_LENGTH;
    }
    *cache = (r1_structured_log_cache){
        .bytes = bytes,
        .capacity = (uint32_t)capacity,
        .mode = R1_STRUCTURED_LOG_MODE_STORAGE,
        .severity_threshold = 3u,
        .initialized = true,
    };
    return R1_OK;
}

size_t r1_structured_log_cache_count(
    const r1_structured_log_cache *cache) {
    if (!structured_log_ready(cache)) {
        return 0u;
    }
    return cache->write_index < cache->read_index
        ? cache->capacity - (cache->read_index - cache->write_index)
        : cache->write_index - cache->read_index;
}

size_t r1_structured_log_cache_free(
    const r1_structured_log_cache *cache) {
    return structured_log_ready(cache)
        ? cache->capacity - r1_structured_log_cache_count(cache) : 0u;
}

r1_error r1_structured_log_cache_read(
    r1_structured_log_cache *cache, uint8_t *output, size_t length,
    bool consume) {
    if (!structured_log_ready(cache) || (length > 0u && output == NULL)) {
        return R1_ERROR_ARGUMENT;
    }
    if (length > r1_structured_log_cache_count(cache)) {
        return R1_ERROR_LENGTH;
    }
    const size_t first = length < cache->capacity - cache->read_index
        ? length : cache->capacity - cache->read_index;
    if (first > 0u) {
        for (size_t index = 0u; index < first; ++index) {
            output[index] = cache->bytes[cache->read_index + index];
        }
    }
    for (size_t index = first; index < length; ++index) {
        output[index] = cache->bytes[index - first];
    }
    if (consume && length > 0u) {
        cache->read_index = (uint32_t)(
            (cache->read_index + length) % cache->capacity);
    }
    return R1_OK;
}

r1_error r1_structured_log_cache_peek(
    const r1_structured_log_cache *cache, size_t offset,
    uint8_t *output, size_t length) {
    if (!structured_log_ready(cache) || (length > 0u && output == NULL)) {
        return R1_ERROR_ARGUMENT;
    }
    const size_t count = r1_structured_log_cache_count(cache);
    if (offset > count || length > count - offset) {
        return R1_ERROR_LENGTH;
    }
    const size_t start = (cache->read_index + offset) % cache->capacity;
    const size_t first = length < cache->capacity - start
        ? length : cache->capacity - start;
    for (size_t index = 0u; index < first; ++index) {
        output[index] = cache->bytes[start + index];
    }
    for (size_t index = first; index < length; ++index) {
        output[index] = cache->bytes[index - first];
    }
    return R1_OK;
}

static r1_structured_log_action structured_log_action(
    const r1_structured_log_cache *cache) {
    const size_t count = r1_structured_log_cache_count(cache);
    if ((cache->mode & R1_STRUCTURED_LOG_MODE_IMMEDIATE) != 0u &&
        count >= R1_STRUCTURED_LOG_IMMEDIATE_BYTES) {
        return R1_STRUCTURED_LOG_ACTION_IMMEDIATE_READY;
    }
    if ((cache->mode & R1_STRUCTURED_LOG_MODE_STORAGE) != 0u &&
        count >= R1_STRUCTURED_LOG_PERSIST_BYTES) {
        return R1_STRUCTURED_LOG_ACTION_PERSIST_READY;
    }
    return R1_STRUCTURED_LOG_ACTION_NONE;
}

r1_error r1_structured_log_cache_append(
    r1_structured_log_cache *cache, const uint8_t *input, size_t length,
    r1_structured_log_action *action) {
    if (!structured_log_ready(cache) || input == NULL || action == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    *action = structured_log_action(cache);
    const size_t free_bytes = r1_structured_log_cache_free(cache);
    /* The stock comparison is strict after subtracting its sentinel byte,
     * leaving two bytes unused at maximum occupancy. */
    if (free_bytes < 2u || length >= free_bytes - 1u) {
        return R1_ERROR_CAPACITY;
    }
    const size_t first = length < cache->capacity - cache->write_index
        ? length : cache->capacity - cache->write_index;
    for (size_t index = 0u; index < first; ++index) {
        cache->bytes[cache->write_index + index] = input[index];
    }
    for (size_t index = first; index < length; ++index) {
        cache->bytes[index - first] = input[index];
    }
    cache->write_index = (uint32_t)(
        (cache->write_index + length) % cache->capacity);
    *action = structured_log_action(cache);
    return R1_OK;
}

void r1_structured_log_threshold_set(
    r1_structured_log_cache *cache, uint8_t threshold) {
    if (cache != NULL) {
        cache->severity_threshold = threshold;
    }
}

uint8_t r1_structured_log_mode_get(
    const r1_structured_log_cache *cache) {
    return cache == NULL ? 0u : cache->mode;
}

void r1_structured_log_mode_set(
    r1_structured_log_cache *cache, uint8_t mode) {
    if (cache != NULL) {
        cache->mode = mode;
    }
}

static bool structured_log_filtered(
    const r1_structured_log_cache *cache, uint32_t metadata) {
    const uint8_t severity = (uint8_t)((metadata & UINT32_C(0x1fffffff)) >> 26u);
    if ((cache->mode & R1_STRUCTURED_LOG_MODE_IMMEDIATE) != 0u) {
        return severity > 5u;
    }
    return (cache->mode & R1_STRUCTURED_LOG_MODE_STORAGE) != 0u &&
        cache->severity_threshold < severity;
}

static void structured_log_prefix(
    r1_structured_log_cache *cache, uint8_t *record,
    uint32_t metadata, uint32_t tick, uint32_t timestamp) {
    record[0] = UINT8_C(0x7b);
    record[1] = cache->sequence++;
    const uint16_t tick_header = (uint16_t)(
        UINT16_C(0xdc00) + (uint16_t)(tick % UINT32_C(1000)));
    record[2] = (uint8_t)tick_header;
    record[3] = (uint8_t)(tick_header >> 8u);
    storage_write_u32(record + 4u, timestamp);
    storage_write_u32(record + 8u, metadata);
}

static size_t bounded_string_length(const char *string) {
    if (string == NULL) {
        return 0u;
    }
    size_t length = 0u;
    while (string[length] != '\0') {
        ++length;
    }
    return length;
}

static void structured_log_copy_string(
    uint8_t output[R1_STRUCTURED_LOG_STRING_BYTES], const char *string,
    bool retain_tail) {
    if (string == NULL) {
        return;
    }
    const size_t length = bounded_string_length(string);
    const size_t copied = length < R1_STRUCTURED_LOG_STRING_BYTES
        ? length : R1_STRUCTURED_LOG_STRING_BYTES;
    const char *source = string;
    if (retain_tail && length > copied) {
        source += length - copied;
    }
    for (size_t index = 0u; index < copied; ++index) {
        output[index] = (uint8_t)source[index];
    }
}

static r1_error structured_log_emit(
    r1_structured_log_cache *cache, uint8_t *record, size_t length,
    r1_structured_log_encode_result *result) {
    if (length > UINT16_MAX) {
        return R1_ERROR_LENGTH;
    }
    result->record_bytes = (uint16_t)length;
    const r1_error error = r1_structured_log_cache_append(
        cache, record, length, &result->action);
    result->appended = error == R1_OK;
    return error;
}

r1_error r1_structured_log_encode_typed(
    r1_structured_log_cache *cache, uint32_t metadata,
    uint32_t tick, uint32_t timestamp,
    const r1_structured_log_argument *arguments, size_t argument_count,
    r1_structured_log_encode_result *result) {
    if (!structured_log_ready(cache) || result == NULL ||
        (argument_count > 0u && arguments == NULL)) {
        return R1_ERROR_ARGUMENT;
    }
    *result = (r1_structured_log_encode_result){0};
    if (structured_log_filtered(cache, metadata)) {
        result->filtered = true;
        return R1_OK;
    }
    const size_t declared_count = (metadata & UINT32_C(0x03ffffff)) >> 22u;
    const size_t encoded_count = declared_count < 8u ? declared_count : 8u;
    if (argument_count < encoded_count) {
        return R1_ERROR_ARGUMENT;
    }
    uint8_t record[R1_STRUCTURED_LOG_RECORD_BYTES] = {0};
    structured_log_prefix(cache, record, metadata, tick, timestamp);
    const uint8_t record_mode = (uint8_t)(metadata >> 29u);
    size_t length = R1_STRUCTURED_LOG_PREFIX_BYTES;
    if (record_mode == 4u) {
        const size_t string_count = encoded_count < 2u ? encoded_count : 2u;
        for (size_t index = 0u; index < string_count; ++index) {
            if (arguments[index].type != R1_STRUCTURED_LOG_ARGUMENT_STRING) {
                return R1_ERROR_ARGUMENT;
            }
            structured_log_copy_string(
                record + length, arguments[index].value.string, false);
            length += R1_STRUCTURED_LOG_STRING_BYTES;
        }
    } else if (record_mode == 6u && encoded_count > 0u) {
        if (arguments[0].type != R1_STRUCTURED_LOG_ARGUMENT_STRING) {
            return R1_ERROR_ARGUMENT;
        }
        structured_log_copy_string(
            record + length, arguments[0].value.string, false);
        length += R1_STRUCTURED_LOG_STRING_BYTES;
        const size_t word_count = encoded_count < 5u ? encoded_count : 5u;
        for (size_t index = 1u; index < word_count; ++index) {
            if (arguments[index].type != R1_STRUCTURED_LOG_ARGUMENT_U32) {
                return R1_ERROR_ARGUMENT;
            }
            storage_write_u32(record + length, arguments[index].value.u32);
            length += sizeof(uint32_t);
        }
    } else {
        for (size_t index = 0u; index < encoded_count; ++index) {
            if (arguments[index].type != R1_STRUCTURED_LOG_ARGUMENT_U32) {
                return R1_ERROR_ARGUMENT;
            }
            storage_write_u32(record + length, arguments[index].value.u32);
            length += sizeof(uint32_t);
        }
    }
    return structured_log_emit(cache, record, length, result);
}

static bool structured_log_format_digit(char value) {
    return value >= '0' && value <= '9';
}

static bool structured_log_format_flag(char value) {
    return value == '0' || value == '-' || value == '+' ||
        value == ' ' || value == '#';
}

static r1_error structured_log_skip_star_argument(
    const r1_structured_log_argument *arguments, size_t argument_count,
    size_t *argument_index) {
    if (*argument_index >= argument_count ||
        arguments[*argument_index].type != R1_STRUCTURED_LOG_ARGUMENT_U32) {
        return R1_ERROR_ARGUMENT;
    }
    *argument_index += 1u;
    return R1_OK;
}

r1_error r1_structured_log_encode_format(
    r1_structured_log_cache *cache, uint32_t metadata,
    uint32_t tick, uint32_t timestamp, const char *format,
    const r1_structured_log_argument *arguments, size_t argument_count,
    r1_structured_log_encode_result *result) {
    if (!structured_log_ready(cache) || format == NULL || result == NULL ||
        (argument_count > 0u && arguments == NULL)) {
        return R1_ERROR_ARGUMENT;
    }
    *result = (r1_structured_log_encode_result){0};
    if (structured_log_filtered(cache, metadata)) {
        result->filtered = true;
        return R1_OK;
    }

    uint8_t record[R1_STRUCTURED_LOG_RECORD_BYTES] = {0};
    structured_log_prefix(cache, record, metadata, tick, timestamp);
    size_t payload_bytes = 0u;
    size_t argument_index = 0u;
    uint8_t conversions = 0u;
    const uint8_t declared_conversions = (uint8_t)(
        (metadata & UINT32_C(0x03ffffff)) >> 22u);

    for (size_t format_index = 0u;
         format[format_index] != '\0' &&
             conversions < declared_conversions && payload_bytes < 32u;
         ++format_index) {
        if (format[format_index] != '%') {
            continue;
        }
        ++format_index;
        if (format[format_index] == '%') {
            continue;
        }
        while (structured_log_format_flag(format[format_index])) {
            ++format_index;
        }
        if (format[format_index] == '*') {
            const r1_error error = structured_log_skip_star_argument(
                arguments, argument_count, &argument_index);
            if (error != R1_OK) {
                return error;
            }
            ++format_index;
        } else {
            while (structured_log_format_digit(format[format_index])) {
                ++format_index;
            }
        }
        if (format[format_index] == '.') {
            ++format_index;
            if (format[format_index] == '*') {
                const r1_error error = structured_log_skip_star_argument(
                    arguments, argument_count, &argument_index);
                if (error != R1_OK) {
                    return error;
                }
                ++format_index;
            } else {
                while (structured_log_format_digit(format[format_index])) {
                    ++format_index;
                }
            }
        }
        bool wide = false;
        if (format[format_index] == 'l') {
            ++format_index;
            if (format[format_index] == 'l') {
                wide = true;
                ++format_index;
            }
        } else if (format[format_index] == 'h') {
            ++format_index;
            if (format[format_index] == 'h') {
                ++format_index;
            }
        }
        const char conversion = format[format_index];
        if (conversion == '\0') {
            break;
        }
        if (argument_index >= argument_count) {
            return R1_ERROR_ARGUMENT;
        }
        const r1_structured_log_argument *const argument =
            &arguments[argument_index++];
        if (conversion == 's') {
            if (argument->type != R1_STRUCTURED_LOG_ARGUMENT_STRING) {
                return R1_ERROR_ARGUMENT;
            }
            if (payload_bytes + R1_STRUCTURED_LOG_STRING_BYTES >
                R1_STRUCTURED_LOG_ARGUMENT_BYTES) {
                break;
            }
            structured_log_copy_string(
                record + R1_STRUCTURED_LOG_PREFIX_BYTES + payload_bytes,
                argument->value.string, true);
            payload_bytes += R1_STRUCTURED_LOG_STRING_BYTES;
        } else {
            if (payload_bytes + sizeof(uint32_t) >
                R1_STRUCTURED_LOG_ARGUMENT_BYTES) {
                break;
            }
            uint32_t captured = 0u;
            if (conversion == 'f' || conversion == 'F') {
                if (argument->type != R1_STRUCTURED_LOG_ARGUMENT_FLOAT64) {
                    return R1_ERROR_ARGUMENT;
                }
                union {
                    float floating;
                    uint32_t bits;
                } converted = {.floating = (float)argument->value.floating};
                captured = converted.bits;
            } else if (wide) {
                if (argument->type != R1_STRUCTURED_LOG_ARGUMENT_U64) {
                    return R1_ERROR_ARGUMENT;
                }
                captured = (uint32_t)argument->value.u64;
            } else {
                if (argument->type != R1_STRUCTURED_LOG_ARGUMENT_U32) {
                    return R1_ERROR_ARGUMENT;
                }
                captured = argument->value.u32;
            }
            storage_write_u32(
                record + R1_STRUCTURED_LOG_PREFIX_BYTES + payload_bytes,
                captured);
            payload_bytes += sizeof(uint32_t);
        }
        ++conversions;
    }
    metadata = (metadata & UINT32_C(0xfc3fffff)) |
        ((uint32_t)conversions << 22u);
    storage_write_u32(record + 8u, metadata);
    return structured_log_emit(
        cache, record, R1_STRUCTURED_LOG_PREFIX_BYTES + payload_bytes,
        result);
}

r1_error r1_structured_log_periodic_persist(
    r1_structured_log_cache *cache, r1_log_bin_store *store,
    uint32_t tick, bool export_active,
    uint8_t scratch[R1_STRUCTURED_LOG_PERSIST_BYTES], bool *persisted) {
    if (!structured_log_ready(cache) || store == NULL || scratch == NULL ||
        persisted == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    *persisted = false;
    if (export_active) {
        return R1_OK;
    }
    r1_error error = r1_structured_log_cache_read(
        cache, scratch, R1_STRUCTURED_LOG_PERSIST_BYTES, true);
    if (error == R1_ERROR_LENGTH) {
        return R1_OK;
    }
    if (error != R1_OK) {
        return error;
    }
    /* This ordering and strict unsigned comparison intentionally reproduce
     * 0x000914A0: a page is consumed before the timing gate is checked. */
    if (tick <= cache->last_persist_tick +
            R1_STRUCTURED_LOG_PERSIST_GATE_TICKS) {
        return R1_OK;
    }
    cache->last_persist_tick = tick;
    error = r1_log_bin_write(store, scratch,
                             R1_STRUCTURED_LOG_PERSIST_BYTES);
    if (error == R1_OK) {
        *persisted = true;
    }
    return error;
}

static bool log_export_range_valid(
    const r1_flash *flash, uint32_t offset, uint32_t length) {
    return flash != NULL && offset <= flash->size &&
        length <= flash->size - offset;
}

static bool log_export_probe_erased(const uint8_t probe[4]) {
    return probe[0] == UINT8_MAX && probe[1] == UINT8_MAX &&
        probe[2] == UINT8_MAX && probe[3] == UINT8_MAX;
}

static bool log_export_ep_magic(const uint8_t *bytes, size_t length) {
    for (size_t offset = 0u; offset + R1_EP_RECORD_BYTES <= length;
         offset += R1_EP_RECORD_BYTES) {
        if ((bytes[offset] & UINT8_C(0x0f)) == R1_EP_RECORD_MAGIC) {
            return true;
        }
    }
    return false;
}

static r1_error log_export_crc_flash(
    const r1_flash *flash, uint32_t offset, size_t length,
    uint8_t scratch[R1_LOG_BIN_SECTOR_BYTES], uint32_t *crc,
    bool inspect_ep, bool *ep_magic_present) {
    size_t consumed = 0u;
    while (consumed < length) {
        const size_t chunk = length - consumed < R1_LOG_BIN_SECTOR_BYTES
            ? length - consumed : R1_LOG_BIN_SECTOR_BYTES;
        const r1_error error = r1_flash_read(
            flash, offset + (uint32_t)consumed, scratch, chunk);
        if (error != R1_OK) {
            return error;
        }
        if (inspect_ep && log_export_ep_magic(scratch, chunk)) {
            *ep_magic_present = true;
        }
        *crc = r1_crc32_castagnoli_update(*crc, scratch, chunk);
        consumed += chunk;
    }
    return R1_OK;
}

r1_error r1_log_export_snapshot_prepare(
    r1_log_export_snapshot *snapshot, const r1_flash *flash,
    uint32_t ep_offset, uint32_t log_offset,
    r1_structured_log_cache *cache,
    const uint8_t *crash, size_t crash_length,
    uint8_t scratch[R1_LOG_BIN_SECTOR_BYTES]) {
    if (snapshot == NULL || flash == NULL || !structured_log_ready(cache) ||
        scratch == NULL || (crash_length > 0u && crash == NULL)) {
        return R1_ERROR_ARGUMENT;
    }
    *snapshot = (r1_log_export_snapshot){0};
    if (!log_export_range_valid(flash, ep_offset, R1_EP_PARTITION_BYTES) ||
        !log_export_range_valid(
            flash, log_offset, R1_LOG_BIN_PARTITION_BYTES) ||
        crash_length > UINT16_MAX) {
        return R1_ERROR_LENGTH;
    }
    const size_t cache_length = r1_structured_log_cache_count(cache);
    if (cache_length > UINT16_MAX) {
        return R1_ERROR_LENGTH;
    }

    uint8_t first_erased = R1_LOG_BIN_SECTOR_COUNT;
    bool sector_erased[R1_LOG_BIN_SECTOR_COUNT] = {false};
    uint8_t probe[4];
    for (uint8_t sector = 0u; sector < R1_LOG_BIN_SECTOR_COUNT; ++sector) {
        const r1_error error = r1_flash_read(
            flash, log_offset + (uint32_t)sector * R1_LOG_BIN_SECTOR_BYTES +
                R1_LOG_BIN_ERASED_PROBE_OFFSET,
            probe, sizeof probe);
        if (error != R1_OK) {
            return error;
        }
        sector_erased[sector] = log_export_probe_erased(probe);
        if (sector_erased[sector] && first_erased == R1_LOG_BIN_SECTOR_COUNT) {
            first_erased = sector;
        }
    }

    uint8_t log_count = 0u;
    const uint8_t start = first_erased < R1_LOG_BIN_SECTOR_COUNT
        ? (uint8_t)((first_erased + 1u) % R1_LOG_BIN_SECTOR_COUNT) : 0u;
    for (uint8_t step = 0u; step < R1_LOG_BIN_SECTOR_COUNT; ++step) {
        const uint8_t sector = (uint8_t)(
            (start + step) % R1_LOG_BIN_SECTOR_COUNT);
        if (!sector_erased[sector]) {
            snapshot->log_sector_order[log_count++] = sector;
        }
    }

    snapshot->flash = flash;
    snapshot->cache = cache;
    snapshot->crash = crash;
    snapshot->ep_offset = ep_offset;
    snapshot->log_offset = log_offset;
    snapshot->info.log_sector_count = log_count;
    snapshot->info.cache_bytes = (uint16_t)cache_length;
    snapshot->info.crash_bytes = (uint16_t)crash_length;

    uint32_t crc = 0u;
    r1_error error = log_export_crc_flash(
        flash, ep_offset, R1_EP_PARTITION_BYTES, scratch, &crc, true,
        &snapshot->info.ep_magic_present);
    if (error != R1_OK) {
        return error;
    }
    snapshot->info.eligible = log_count > 0u ||
        snapshot->info.ep_magic_present;
    if (!snapshot->info.eligible) {
        return R1_OK;
    }
    for (uint8_t index = 0u; index < log_count; ++index) {
        error = log_export_crc_flash(
            flash,
            log_offset + (uint32_t)snapshot->log_sector_order[index] *
                R1_LOG_BIN_SECTOR_BYTES,
            R1_LOG_BIN_SECTOR_BYTES, scratch, &crc, false,
            &snapshot->info.ep_magic_present);
        if (error != R1_OK) {
            return error;
        }
    }
    size_t cache_offset = 0u;
    while (cache_offset < cache_length) {
        const size_t chunk = cache_length - cache_offset <
                R1_LOG_BIN_SECTOR_BYTES
            ? cache_length - cache_offset : R1_LOG_BIN_SECTOR_BYTES;
        error = r1_structured_log_cache_peek(
            cache, cache_offset, scratch, chunk);
        if (error != R1_OK) {
            return error;
        }
        crc = r1_crc32_castagnoli_update(crc, scratch, chunk);
        cache_offset += chunk;
    }
    crc = r1_crc32_castagnoli_update(crc, crash, crash_length);
    snapshot->info.total_bytes = R1_EP_PARTITION_BYTES +
        (uint32_t)log_count * R1_LOG_BIN_SECTOR_BYTES +
        (uint32_t)cache_length + (uint32_t)crash_length;
    snapshot->info.checksum = crc;
    snapshot->active = true;
    return R1_OK;
}

static r1_error log_export_copy_flash_segment(
    const r1_log_export_snapshot *snapshot, uint32_t segment_offset,
    uint32_t segment_length, uint32_t *virtual_offset,
    uint8_t **output, size_t *remaining) {
    if (*virtual_offset >= segment_length || *remaining == 0u) {
        if (*virtual_offset >= segment_length) {
            *virtual_offset -= segment_length;
        }
        return R1_OK;
    }
    const size_t copied = *remaining < segment_length - *virtual_offset
        ? *remaining : segment_length - *virtual_offset;
    const r1_error error = r1_flash_read(
        snapshot->flash, segment_offset + *virtual_offset, *output, copied);
    if (error != R1_OK) {
        return error;
    }
    *output += copied;
    *remaining -= copied;
    *virtual_offset = 0u;
    return R1_OK;
}

r1_error r1_log_export_snapshot_read(
    const r1_log_export_snapshot *snapshot, uint32_t offset,
    uint8_t *output, size_t length) {
    if (snapshot == NULL || !snapshot->active ||
        (length > 0u && output == NULL)) {
        return R1_ERROR_ARGUMENT;
    }
    if (offset > snapshot->info.total_bytes ||
        length > snapshot->info.total_bytes - offset) {
        return R1_ERROR_LENGTH;
    }
    uint32_t virtual_offset = offset;
    size_t remaining = length;
    uint8_t *cursor = output;
    r1_error error = log_export_copy_flash_segment(
        snapshot, snapshot->ep_offset, R1_EP_PARTITION_BYTES,
        &virtual_offset, &cursor, &remaining);
    if (error != R1_OK) {
        return error;
    }
    for (uint8_t index = 0u;
         index < snapshot->info.log_sector_count && remaining > 0u; ++index) {
        error = log_export_copy_flash_segment(
            snapshot,
            snapshot->log_offset +
                (uint32_t)snapshot->log_sector_order[index] *
                    R1_LOG_BIN_SECTOR_BYTES,
            R1_LOG_BIN_SECTOR_BYTES, &virtual_offset, &cursor, &remaining);
        if (error != R1_OK) {
            return error;
        }
    }
    if (remaining > 0u) {
        if (virtual_offset >= snapshot->info.cache_bytes) {
            virtual_offset -= snapshot->info.cache_bytes;
        } else {
            const size_t copied = remaining <
                    snapshot->info.cache_bytes - virtual_offset
                ? remaining : snapshot->info.cache_bytes - virtual_offset;
            error = r1_structured_log_cache_peek(
                snapshot->cache, virtual_offset, cursor, copied);
            if (error != R1_OK) {
                return error;
            }
            cursor += copied;
            remaining -= copied;
            virtual_offset = 0u;
        }
    }
    if (remaining > 0u) {
        if (virtual_offset > snapshot->info.crash_bytes ||
            remaining > snapshot->info.crash_bytes - virtual_offset) {
            return R1_ERROR_STATE;
        }
        for (size_t index = 0u; index < remaining; ++index) {
            cursor[index] = snapshot->crash[virtual_offset + index];
        }
        remaining = 0u;
    }
    return remaining == 0u ? R1_OK : R1_ERROR_STATE;
}

void r1_log_export_snapshot_finish(r1_log_export_snapshot *snapshot) {
    if (snapshot != NULL) {
        snapshot->active = false;
    }
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

/* Recovered stored-sleep iterator/report callback policy. Header inspection,
 * compact-packet expansion, logging, allocation, BLE transport, and ACK
 * registration remain external. */
r1_error r1_sleep_sync_plan_report_callback(
    bool context_present, uint8_t synchronization_flag,
    uint8_t report_type, uint16_t stage_count,
    r1_sleep_sync_report_plan *plan) {
    if (plan == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    *plan = (r1_sleep_sync_report_plan){
        .context_present = context_present,
    };
    if (!context_present) {
        return R1_OK;
    }

    plan->callback_result = true;
    if (synchronization_flag == 1u) {
        plan->skip_synchronized_record = true;
        return R1_OK;
    }

    plan->invoke_packet_builder = true;
    plan->report_type = report_type;
    plan->stage_count = stage_count;
    plan->model_identifier = R1_SLEEP_SYNC_MODEL_IDENTIFIER;
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

r1_error r1_storage_task_plan_startup(
    bool queue_created, r1_storage_task_startup_plan *plan) {
    if (plan == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    *plan = (r1_storage_task_startup_plan){
        .queue_create_failed = !queue_created,
        .enter_fail_stop = !queue_created,
        .queue_capacity = R1_STORAGE_TASK_QUEUE_CAPACITY,
        .queue_record_bytes = R1_STORAGE_TASK_RECORD_BYTES,
        .sync_group = R1_STORAGE_TASK_SYNC_GROUP,
        .registry_name = "storage",
        .watchdog_ticks = R1_STORAGE_TASK_WATCHDOG_TICKS,
    };
    if (!queue_created) {
        return R1_OK;
    }
    static const r1_storage_task_startup_action actions[] = {
        R1_STORAGE_TASK_BACKEND_INITIALIZE,
        R1_STORAGE_TASK_SCHEDULE_DELAYED_EVENT,
    };
    for (size_t index = 0u;
         index < R1_STORAGE_TASK_STARTUP_ACTION_COUNT; ++index) {
        plan->actions[index] = actions[index];
    }
    plan->action_count = R1_STORAGE_TASK_STARTUP_ACTION_COUNT;
    return R1_OK;
}

r1_error r1_service_task_plan_startup(
    bool queue_created, r1_service_task_startup_plan *plan) {
    if (plan == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    *plan = (r1_service_task_startup_plan){
        .queue_create_failed = !queue_created,
        .enter_fail_stop = !queue_created,
        .queue_capacity = R1_SERVICE_TASK_QUEUE_CAPACITY,
        .queue_record_bytes = R1_SERVICE_TASK_RECORD_BYTES,
        .sync_group = R1_SERVICE_TASK_SYNC_GROUP,
        .registry_name = "service",
        .watchdog_ticks = R1_SERVICE_TASK_WATCHDOG_TICKS,
    };
    if (!queue_created) {
        return R1_OK;
    }
    static const r1_service_task_startup_action actions[] = {
        R1_SERVICE_TASK_HARDWARE_INITIALIZE,
        R1_SERVICE_TASK_HEALTH_DATABASE_START,
        R1_SERVICE_TASK_HEART_RATE_CACHE_REFRESH,
        R1_SERVICE_TASK_SPO2_CACHE_REFRESH,
        R1_SERVICE_TASK_TEMPERATURE_CACHE_REFRESH,
        R1_SERVICE_TASK_STRESS_CACHE_REFRESH,
        R1_SERVICE_TASK_ACTIVITY_CACHE_REFRESH,
        R1_SERVICE_TASK_SLEEP_DATABASE_START,
        R1_SERVICE_TASK_HRV_CACHE_REFRESH,
        R1_SERVICE_TASK_PROTOCOL_STATE_RESET,
    };
    for (size_t index = 0u;
         index < R1_SERVICE_TASK_STARTUP_ACTION_COUNT; ++index) {
        plan->actions[index] = actions[index];
    }
    plan->action_count = R1_SERVICE_TASK_STARTUP_ACTION_COUNT;
    return R1_OK;
}

r1_error r1_service_task_plan_flags(
    uint32_t flags, r1_service_task_flag_plan *plan) {
    if (plan == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    *plan = (r1_service_task_flag_plan){
        .observed_flags = flags,
        .provider_wait_error = flags == 0u || (flags & UINT32_C(0x80000000)) != 0u,
        .dispatch_event_record =
            (flags & R1_SERVICE_TASK_DISPATCH_FLAG) != 0u,
        .signal_suspend = (flags & R1_SERVICE_TASK_SUSPEND_FLAG) != 0u,
        .enter_suspend_wait = (flags & R1_SERVICE_TASK_SUSPEND_FLAG) != 0u,
        .wait_again = (flags & R1_SERVICE_TASK_SUSPEND_FLAG) == 0u,
    };
    if (plan->provider_wait_error) {
        plan->dispatch_event_record = false;
        plan->signal_suspend = false;
        plan->enter_suspend_wait = false;
        plan->wait_again = true;
    }
    return R1_OK;
}

r1_error r1_storage_task_plan_flags(
    uint32_t flags, r1_storage_task_flag_plan *plan) {
    if (plan == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    *plan = (r1_storage_task_flag_plan){
        .observed_flags = flags,
        .provider_wait_error = flags == 0u || (flags & UINT32_C(0x80000000)) != 0u,
        .dispatch_event_record =
            (flags & R1_STORAGE_TASK_DISPATCH_FLAG) != 0u,
        .signal_suspend = (flags & R1_STORAGE_TASK_SUSPEND_FLAG) != 0u,
        .enter_suspend_wait = (flags & R1_STORAGE_TASK_SUSPEND_FLAG) != 0u,
        .wait_again = (flags & R1_STORAGE_TASK_SUSPEND_FLAG) == 0u,
    };
    if (plan->provider_wait_error) {
        plan->dispatch_event_record = false;
        plan->signal_suspend = false;
        plan->enter_suspend_wait = false;
        plan->wait_again = true;
    }
    return R1_OK;
}
