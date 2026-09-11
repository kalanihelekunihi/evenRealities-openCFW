/*
 * The little filesystem
 *
 * Copyright (c) 2022, The littlefs authors.
 * Copyright (c) 2017, Arm Limited. All rights reserved.
 * SPDX-License-Identifier: BSD-3-Clause
 *
 * Production ABI for an adaptation of littlefs v2.10.1 lfs_tag_isdelete().
 * The private upstream lfs_tag_t is exactly uint32_t; this isolated boundary
 * intentionally exposes no other littlefs internals.
 */

#ifndef OPEN_CFW_RUNTIME_LITTLEFS_TAG_ISDELETE_H
#define OPEN_CFW_RUNTIME_LITTLEFS_TAG_ISDELETE_H

#include <stdbool.h>
#include <stdint.h>

typedef uint32_t open_cfw_littlefs_isdelete_tag_t;

_Static_assert(
    sizeof(open_cfw_littlefs_isdelete_tag_t) == 4U,
    "littlefs lfs_tag_t width changed"
);
_Static_assert(sizeof(int32_t) == 4U, "littlefs requires 32-bit int32_t");
_Static_assert(sizeof(bool) == 1U, "reviewed littlefs ABI requires 8-bit bool");

bool open_cfw_littlefs_tag_isdelete(open_cfw_littlefs_isdelete_tag_t tag);

#endif
