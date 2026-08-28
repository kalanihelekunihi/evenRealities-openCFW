/*
 * SPDX-License-Identifier: MIT
 *
 * Metadata-only admission boundary.  No FreeType, Adobe, or SEGGER source is
 * copied into this file and no stock-address replacement is enabled here.
 */
#ifndef OPEN_CFW_G2_NONE_SOURCE_ADMISSION_H
#define OPEN_CFW_G2_NONE_SOURCE_ADMISSION_H

#include <stddef.h>
#include <stdint.h>

typedef enum {
    OPEN_CFW_NONE_PROVIDER_FREETYPE_FTL = 1,
    OPEN_CFW_NONE_PROVIDER_SEGGER_RTT_UPSTREAM = 2,
    OPEN_CFW_NONE_PROVIDER_TYPED_EXTERNAL = 3
} open_cfw_none_provider_kind_t;

typedef struct {
    open_cfw_none_provider_kind_t kind;
    uint32_t function_count;
    uint32_t image_bytes;
    uint8_t source_materialized;
    uint8_t binary_overlay_admitted;
} open_cfw_none_provider_t;

extern const open_cfw_none_provider_t open_cfw_none_source_providers[3];
extern const size_t open_cfw_none_source_provider_count;

int open_cfw_none_source_admission_validate(void);
const open_cfw_none_provider_t *
open_cfw_none_source_provider(open_cfw_none_provider_kind_t kind);

#endif
