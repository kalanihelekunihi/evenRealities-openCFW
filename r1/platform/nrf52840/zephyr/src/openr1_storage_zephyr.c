#include "openr1_storage_zephyr.h"

#include <errno.h>
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#include <zephyr/kernel.h>
#include <zephyr/storage/flash_map.h>

#define OPENR1_STORAGE_BYTES UINT32_C(0x00024000)
#define OPENR1_STORAGE_PARTITION FIXED_PARTITION_ID(openr1_data_partition)

static const struct flash_area *storage_area;
static struct k_mutex storage_mutex;
static struct k_mutex log_mutex;
static r1_flash storage_flash;
static r1_log_bin_store log_store;
static r1_structured_log_cache structured_log_cache;
static r1_log_export_snapshot diagnostic_export_snapshot;
static uint8_t structured_log_bytes[R1_STRUCTURED_LOG_CACHE_BYTES];
static uint32_t structured_log_scratch_words[
    R1_STRUCTURED_LOG_PERSIST_BYTES / sizeof(uint32_t)];
static bool storage_ready;
static r1_ep_scan_result ep_scan_result;
static bool ep_scan_ready;
static bool diagnostic_export_active;

static bool storage_range_valid(uint32_t offset, size_t length) {
    return length <= UINT32_MAX && offset <= OPENR1_STORAGE_BYTES &&
        (uint32_t)length <= OPENR1_STORAGE_BYTES - offset;
}

static bool storage_lock(void) {
    return storage_ready && !k_is_in_isr() &&
        k_mutex_lock(&storage_mutex, K_FOREVER) == 0;
}

static bool storage_read(void *context, uint32_t offset,
                         uint8_t *output, size_t length) {
    (void)context;
    if (!storage_range_valid(offset, length) ||
        (length > 0u && output == NULL) || !storage_lock()) {
        return false;
    }
    const int result = length == 0u ? 0 : flash_area_read(
        storage_area, (off_t)offset, output, length);
    (void)k_mutex_unlock(&storage_mutex);
    return result == 0;
}

static bool storage_program(void *context, uint32_t offset,
                            const uint8_t *input, size_t length) {
    (void)context;
    if (!storage_range_valid(offset, length) ||
        (length > 0u && input == NULL) || !storage_lock()) {
        return false;
    }
    const uint32_t alignment = flash_area_align(storage_area);
    const bool aligned = alignment != 0u &&
        offset % alignment == 0u && length % alignment == 0u;
    const int result = length == 0u ? 0 :
        (aligned ? flash_area_write(storage_area, (off_t)offset, input, length)
                 : -EINVAL);
    (void)k_mutex_unlock(&storage_mutex);
    return result == 0;
}

static bool storage_erase(void *context, uint32_t offset, size_t length) {
    (void)context;
    if (!storage_range_valid(offset, length) ||
        offset % R1_FLASH_PAGE_BYTES != 0u ||
        length % R1_FLASH_PAGE_BYTES != 0u || !storage_lock()) {
        return false;
    }
    const int result = length == 0u ? 0 :
        flash_area_erase(storage_area, (off_t)offset, length);
    (void)k_mutex_unlock(&storage_mutex);
    return result == 0;
}

int openr1_storage_zephyr_initialize(void) {
    if (storage_ready) {
        return 0;
    }
    const int result = flash_area_open(OPENR1_STORAGE_PARTITION, &storage_area);
    if (result != 0) {
        return result;
    }
    if (storage_area == NULL || storage_area->fa_size != OPENR1_STORAGE_BYTES ||
        storage_area->fa_off != UINT32_C(0x000d4000) ||
        flash_area_align(storage_area) > sizeof(uint32_t)) {
        flash_area_close(storage_area);
        storage_area = NULL;
        return -EINVAL;
    }
    k_mutex_init(&storage_mutex);
    k_mutex_init(&log_mutex);
    storage_flash = (r1_flash){
        .context = NULL,
        .size = OPENR1_STORAGE_BYTES,
        .read = storage_read,
        .program = storage_program,
        .erase = storage_erase,
    };
    storage_ready = true;
    const r1_partition *const ep_partition = r1_storage_partition("ep.bin");
    r1_ep_initialization_plan ep_plan;
    const r1_error plan_error = r1_ep_plan_initialization(
        false, ep_partition != NULL, true,
        ep_partition == NULL ? 0u : ep_partition->length, &ep_plan);
    const r1_error scan_error = plan_error == R1_OK && ep_plan.initialized &&
            ep_plan.scan_cursor
        ? r1_ep_scan_flash_cursor(
            &storage_flash, ep_partition->offset, &ep_scan_result)
        : R1_ERROR_STATE;
    if (scan_error != R1_OK) {
        storage_ready = false;
        flash_area_close(storage_area);
        storage_area = NULL;
        return -EIO;
    }
    ep_scan_ready = true;
    const r1_partition *const log_partition =
        r1_storage_partition("log.bin");
    if (log_partition == NULL || r1_log_bin_bind(
            &log_store, &storage_flash, log_partition->offset,
            log_partition->length) != R1_OK ||
            r1_log_bin_initialize(&log_store) != R1_OK ||
            r1_structured_log_cache_initialize(
                &structured_log_cache, structured_log_bytes,
                sizeof structured_log_bytes) != R1_OK) {
        ep_scan_ready = false;
        storage_ready = false;
        flash_area_close(storage_area);
        storage_area = NULL;
        return -EIO;
    }
    return 0;
}

r1_flash *openr1_storage_zephyr_flash(void) {
    return storage_ready ? &storage_flash : NULL;
}

bool openr1_storage_zephyr_ep_scan(r1_ep_scan_result *result) {
    if (!storage_ready || !ep_scan_ready || result == NULL) {
        return false;
    }
    *result = ep_scan_result;
    return true;
}

bool openr1_storage_zephyr_log_append(
    const uint8_t *input, size_t length) {
    if (!storage_ready || input == NULL || k_is_in_isr() ||
        k_mutex_lock(&log_mutex, K_FOREVER) != 0) {
        return false;
    }
    const bool written = !diagnostic_export_active &&
        r1_log_bin_write(&log_store, input, length) == R1_OK;
    (void)k_mutex_unlock(&log_mutex);
    return written;
}

uint16_t openr1_storage_zephyr_log_sector_count(void) {
    return storage_ready ? r1_log_bin_sector_count(&log_store) : 0u;
}

static uint32_t structured_log_metadata(
    uint8_t severity, const char *format, size_t argument_count) {
    return ((uint32_t)(severity & UINT8_C(7)) << 26u) |
        ((uint32_t)(argument_count > 15u ? 15u : argument_count) << 22u) |
        ((uint32_t)(uintptr_t)format & UINT32_C(0x003fffff));
}

bool openr1_storage_zephyr_structured_log_typed(
    uint8_t severity, const char *format,
    const r1_structured_log_argument *arguments, size_t argument_count) {
    if (!storage_ready || format == NULL || k_is_in_isr() ||
        k_mutex_lock(&log_mutex, K_FOREVER) != 0) {
        return false;
    }
    r1_structured_log_encode_result result;
    const uint32_t tick = k_uptime_get_32();
    const bool encoded = !diagnostic_export_active &&
        r1_structured_log_encode_typed(
        &structured_log_cache,
        structured_log_metadata(severity, format, argument_count),
        tick, tick, arguments, argument_count, &result) == R1_OK &&
        (result.appended || result.filtered);
    (void)k_mutex_unlock(&log_mutex);
    return encoded;
}

bool openr1_storage_zephyr_structured_log_format(
    uint8_t severity, const char *format,
    const r1_structured_log_argument *arguments, size_t argument_count) {
    if (!storage_ready || format == NULL || k_is_in_isr() ||
        k_mutex_lock(&log_mutex, K_FOREVER) != 0) {
        return false;
    }
    r1_structured_log_encode_result result;
    const uint32_t tick = k_uptime_get_32();
    const bool encoded = !diagnostic_export_active &&
        r1_structured_log_encode_format(
        &structured_log_cache,
        structured_log_metadata(severity, format, argument_count),
        tick, tick, format, arguments, argument_count, &result) == R1_OK &&
        (result.appended || result.filtered);
    (void)k_mutex_unlock(&log_mutex);
    return encoded;
}

size_t openr1_storage_zephyr_structured_log_count(void) {
    if (!storage_ready || k_is_in_isr() ||
        k_mutex_lock(&log_mutex, K_FOREVER) != 0) {
        return 0u;
    }
    const size_t count = r1_structured_log_cache_count(
        &structured_log_cache);
    (void)k_mutex_unlock(&log_mutex);
    return count;
}

bool openr1_storage_zephyr_structured_log_service(uint32_t now_tick) {
    if (!storage_ready || k_is_in_isr() ||
        k_mutex_lock(&log_mutex, K_FOREVER) != 0) {
        return false;
    }
    bool persisted = false;
    const bool serviced = r1_structured_log_periodic_persist(
        &structured_log_cache, &log_store, now_tick,
        diagnostic_export_active,
        (uint8_t *)structured_log_scratch_words, &persisted) == R1_OK;
    (void)k_mutex_unlock(&log_mutex);
    return serviced;
}

bool openr1_storage_zephyr_diagnostic_export_begin(
    r1_log_export_info *info) {
    if (!storage_ready || info == NULL || k_is_in_isr() ||
        k_mutex_lock(&log_mutex, K_FOREVER) != 0) {
        return false;
    }
    bool prepared = false;
    if (!diagnostic_export_active) {
        diagnostic_export_active = true;
        const r1_partition *const ep = r1_storage_partition("ep.bin");
        const r1_partition *const log = r1_storage_partition("log.bin");
        prepared = ep != NULL && log != NULL &&
            r1_log_export_snapshot_prepare(
                &diagnostic_export_snapshot, &storage_flash,
                ep->offset, log->offset, &structured_log_cache,
                NULL, 0u,
                (uint8_t *)structured_log_scratch_words) == R1_OK &&
            diagnostic_export_snapshot.active &&
            diagnostic_export_snapshot.info.eligible;
        if (prepared) {
            *info = diagnostic_export_snapshot.info;
        } else {
            r1_log_export_snapshot_finish(&diagnostic_export_snapshot);
            diagnostic_export_active = false;
        }
    }
    (void)k_mutex_unlock(&log_mutex);
    return prepared;
}

bool openr1_storage_zephyr_diagnostic_export_read(
    uint32_t offset, uint8_t *output, size_t length) {
    if (!storage_ready || output == NULL || length == 0u ||
        length > R1_EXPORT_MAX_CHUNK_BYTES || k_is_in_isr() ||
        k_mutex_lock(&log_mutex, K_FOREVER) != 0) {
        return false;
    }
    const bool read = diagnostic_export_active &&
        r1_log_export_snapshot_read(
            &diagnostic_export_snapshot, offset, output, length) == R1_OK;
    (void)k_mutex_unlock(&log_mutex);
    return read;
}

void openr1_storage_zephyr_diagnostic_export_finish(void) {
    if (!storage_ready || k_is_in_isr() ||
        k_mutex_lock(&log_mutex, K_FOREVER) != 0) {
        return;
    }
    r1_log_export_snapshot_finish(&diagnostic_export_snapshot);
    diagnostic_export_active = false;
    (void)k_mutex_unlock(&log_mutex);
}

bool openr1_storage_zephyr_diagnostic_export_active(void) {
    if (!storage_ready || k_is_in_isr() ||
        k_mutex_lock(&log_mutex, K_FOREVER) != 0) {
        return false;
    }
    const bool active = diagnostic_export_active;
    (void)k_mutex_unlock(&log_mutex);
    return active;
}

typedef struct {
    bool (*ep_scan)(r1_ep_scan_result *result);
    bool (*log_append)(const uint8_t *input, size_t length);
    uint16_t (*log_sector_count)(void);
    bool (*structured_log_typed)(
        uint8_t severity, const char *format,
        const r1_structured_log_argument *arguments, size_t argument_count);
    bool (*structured_log_format)(
        uint8_t severity, const char *format,
        const r1_structured_log_argument *arguments, size_t argument_count);
    size_t (*structured_log_count)(void);
    bool (*structured_log_service)(uint32_t now_tick);
    bool (*diagnostic_export_begin)(r1_log_export_info *info);
    bool (*diagnostic_export_read)(
        uint32_t offset, uint8_t *output, size_t length);
    void (*diagnostic_export_finish)(void);
} openr1_storage_zephyr_api;

__attribute__((used, section(".openr1_platform_api")))
static const openr1_storage_zephyr_api storage_zephyr_api = {
    .ep_scan = openr1_storage_zephyr_ep_scan,
    .log_append = openr1_storage_zephyr_log_append,
    .log_sector_count = openr1_storage_zephyr_log_sector_count,
    .structured_log_typed = openr1_storage_zephyr_structured_log_typed,
    .structured_log_format = openr1_storage_zephyr_structured_log_format,
    .structured_log_count = openr1_storage_zephyr_structured_log_count,
    .structured_log_service = openr1_storage_zephyr_structured_log_service,
    .diagnostic_export_begin =
        openr1_storage_zephyr_diagnostic_export_begin,
    .diagnostic_export_read = openr1_storage_zephyr_diagnostic_export_read,
    .diagnostic_export_finish = openr1_storage_zephyr_diagnostic_export_finish,
};

uint32_t openr1_storage_zephyr_start_address(void) {
    return storage_ready ? storage_area->fa_off : 0u;
}

uint32_t openr1_storage_zephyr_end_address(void) {
    return storage_ready
        ? storage_area->fa_off + storage_area->fa_size : 0u;
}
