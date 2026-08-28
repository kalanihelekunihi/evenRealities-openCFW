/* SPDX-License-Identifier: MIT */
#ifndef OPENCFW_TOUCH_FLASH_ROW_ADAPTERS_H
#define OPENCFW_TOUCH_FLASH_ROW_ADAPTERS_H

#include <stddef.h>
#include <stdint.h>

#define OPEN_CFW_TOUCH_FLASH_ALIGNMENT_ERROR UINT32_C(0x06160002)

typedef struct {
    uint32_t (*write_row)(void *context, uint32_t address,
                          const uint8_t *row_data);
    void *context;
} open_cfw_touch_flash_row_provider;

uint32_t open_cfw_touch_flash_14b0_zero_rows(
    const open_cfw_touch_flash_row_provider *provider,
    uint32_t start_address,
    uint32_t length);
uint32_t open_cfw_touch_flash_1510_copy_rows(
    const open_cfw_touch_flash_row_provider *provider,
    uint32_t start_address,
    uint32_t length,
    const uint8_t *source);
int open_cfw_touch_flash_1560_copy_callback(
    void *unused,
    const uint8_t *source,
    size_t length,
    uint8_t *destination);

#endif
