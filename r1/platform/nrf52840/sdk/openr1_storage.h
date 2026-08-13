#ifndef OPENR1_NRF52840_SDK_STORAGE_H
#define OPENR1_NRF52840_SDK_STORAGE_H

#include <stdint.h>

#include "sdk_errors.h"

#include "openr1/r1_storage.h"

#define OPENR1_STORAGE_PAGE_COUNT UINT32_C(36)
#define OPENR1_STORAGE_BYTES \
    (OPENR1_STORAGE_PAGE_COUNT * R1_FLASH_PAGE_BYTES)

ret_code_t openr1_storage_initialize(void);
r1_flash *openr1_storage_flash(void);
uint32_t openr1_storage_start_address(void);
/* Returns the exclusive end address used by the recovered R1 layout. */
uint32_t openr1_storage_end_address(void);

#endif
