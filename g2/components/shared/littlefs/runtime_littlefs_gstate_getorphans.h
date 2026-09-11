/*
 * The little filesystem
 *
 * Copyright (c) 2022, The littlefs authors.
 * Copyright (c) 2017, Arm Limited. All rights reserved.
 * SPDX-License-Identifier: BSD-3-Clause
 *
 * Production ABI for an adaptation of littlefs v2.10.1
 * lfs_gstate_getorphans(). The private upstream lfs_gstate_t begins with a
 * uint32_t tag field; this isolated boundary intentionally exposes no other
 * littlefs internals beyond the already admitted lfs_tag_size() leaf it
 * calls.
 */

#ifndef OPEN_CFW_RUNTIME_LITTLEFS_GSTATE_GETORPHANS_H
#define OPEN_CFW_RUNTIME_LITTLEFS_GSTATE_GETORPHANS_H

#include <stdint.h>

_Static_assert(sizeof(uint32_t) == 4U, "littlefs requires 32-bit uint32_t");
_Static_assert(sizeof(uint8_t) == 1U, "littlefs requires 8-bit uint8_t");

uint8_t open_cfw_littlefs_gstate_getorphans(const uint32_t *gstate_tag);

#endif
