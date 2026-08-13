#include "openr1/r1_fal_port.h"

#include <limits.h>

#include "fal.h"

#define R1_FAL_DEVICE_BYTES UINT32_C(0x24000)

static r1_flash *active_flash;

r1_error r1_fal_bind(r1_flash *flash) {
    if (flash == NULL || flash->size < R1_FAL_DEVICE_BYTES) {
        return R1_ERROR_LENGTH;
    }
    active_flash = flash;
    return R1_OK;
}

static int fal_device_initialize(void) {
    return active_flash == NULL ? -1 : 0;
}

static int completed_size(size_t size) {
    return size > INT_MAX ? -1 : (int)size;
}

static int fal_device_read(long offset, uint8_t *output, size_t size) {
    if (active_flash == NULL || offset < 0 ||
        r1_flash_read(active_flash, (uint32_t)offset, output, size) != R1_OK) {
        return -1;
    }
    return completed_size(size);
}

static int fal_device_write(long offset, const uint8_t *input, size_t size) {
    if (active_flash == NULL || offset < 0 ||
        r1_flash_program(active_flash, (uint32_t)offset, input, size) != R1_OK) {
        return -1;
    }
    return completed_size(size);
}

static int fal_device_erase(long offset, size_t size) {
    if (active_flash == NULL || offset < 0 ||
        r1_flash_erase(active_flash, (uint32_t)offset, size) != R1_OK) {
        return -1;
    }
    return completed_size(size);
}

const struct fal_flash_dev r1_fal_flash_device = {
    "device_flash",
    0u,
    R1_FAL_DEVICE_BYTES,
    R1_FLASH_PAGE_BYTES,
    {fal_device_initialize, fal_device_read, fal_device_write, fal_device_erase},
    32u
};
