/*
 * The little filesystem
 *
 * Copyright (c) 2022, The littlefs authors.
 * Copyright (c) 2017, Arm Limited. All rights reserved.
 * SPDX-License-Identifier: BSD-3-Clause
 *
 * Production ABI for an altered adaptation of littlefs v2.10.1
 * lfs_tag_type2(). The private upstream lfs_tag_t is exactly uint32_t; this
 * isolated boundary intentionally exposes no other littlefs internals.
 */

#ifndef OPEN_CFW_RUNTIME_LITTLEFS_TAG_TYPE2_H
#define OPEN_CFW_RUNTIME_LITTLEFS_TAG_TYPE2_H

#include <stdint.h>

typedef uint32_t open_cfw_littlefs_tag_t;

_Static_assert(
    sizeof(open_cfw_littlefs_tag_t) == 4U,
    "littlefs lfs_tag_t width changed"
);
_Static_assert(sizeof(uint32_t) == 4U, "littlefs requires 32-bit uint32_t");
_Static_assert(sizeof(uint16_t) == 2U, "littlefs requires 16-bit uint16_t");

uint16_t open_cfw_littlefs_tag_type2(open_cfw_littlefs_tag_t tag);

#endif
