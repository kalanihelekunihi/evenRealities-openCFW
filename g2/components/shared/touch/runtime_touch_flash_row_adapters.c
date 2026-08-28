/* SPDX-License-Identifier: MIT */
#include <stddef.h>
#include <stdint.h>

#include "runtime_touch_flash_row_adapters.h"

#define OPEN_CFW_TOUCH_FLASH_ROW_BYTES 128u
#define OPEN_CFW_TOUCH_FLASH_SCRATCH_BYTES 512u

uint32_t open_cfw_touch_flash_14b0_zero_rows(
    const open_cfw_touch_flash_row_provider *provider,
    uint32_t start_address,
    uint32_t length)
{
    uint8_t scratch[OPEN_CFW_TOUCH_FLASH_SCRATCH_BYTES];
    uint32_t offset;
    size_t index;

    if (provider == NULL || provider->write_row == NULL ||
            (length % OPEN_CFW_TOUCH_FLASH_ROW_BYTES) != 0u) {
        return OPEN_CFW_TOUCH_FLASH_ALIGNMENT_ERROR;
    }
    for (index = 0u; index < sizeof(scratch); ++index) {
        scratch[index] = 0u;
    }
    for (offset = 0u; offset < length;
            offset += OPEN_CFW_TOUCH_FLASH_ROW_BYTES) {
        (void)provider->write_row(provider->context, start_address + offset,
                                  scratch);
    }
    return 0u;
}

uint32_t open_cfw_touch_flash_1510_copy_rows(
    const open_cfw_touch_flash_row_provider *provider,
    uint32_t start_address,
    uint32_t length,
    const uint8_t *source)
{
    uint32_t offset;

    if (provider == NULL || provider->write_row == NULL || source == NULL ||
            (length % OPEN_CFW_TOUCH_FLASH_ROW_BYTES) != 0u) {
        return OPEN_CFW_TOUCH_FLASH_ALIGNMENT_ERROR;
    }
    for (offset = 0u; offset < length;
            offset += OPEN_CFW_TOUCH_FLASH_ROW_BYTES) {
        (void)provider->write_row(provider->context, start_address + offset,
                                  source + offset);
    }
    return 0u;
}

int open_cfw_touch_flash_1560_copy_callback(
    void *unused,
    const uint8_t *source,
    size_t length,
    uint8_t *destination)
{
    size_t index;

    (void)unused;
    if (source == NULL || destination == NULL) {
        return 0;
    }
    for (index = 0u; index < length; ++index) {
        destination[index] = source[index];
    }
    return 0;
}
