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
static r1_flash storage_flash;
static bool storage_ready;

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
    storage_flash = (r1_flash){
        .context = NULL,
        .size = OPENR1_STORAGE_BYTES,
        .read = storage_read,
        .program = storage_program,
        .erase = storage_erase,
    };
    storage_ready = true;
    return 0;
}

r1_flash *openr1_storage_zephyr_flash(void) {
    return storage_ready ? &storage_flash : NULL;
}

uint32_t openr1_storage_zephyr_start_address(void) {
    return storage_ready ? storage_area->fa_off : 0u;
}

uint32_t openr1_storage_zephyr_end_address(void) {
    return storage_ready
        ? storage_area->fa_off + storage_area->fa_size : 0u;
}
