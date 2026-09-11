/*
 * The little filesystem
 *
 * Copyright (c) 2022, The littlefs authors.
 * Copyright (c) 2017, Arm Limited. All rights reserved.
 * SPDX-License-Identifier: BSD-3-Clause
 *
 * Production ABI for an adaptation of littlefs v2.10.1 lfs_pair_issync().
 * The private upstream lfs_block_t is exactly uint32_t; this isolated
 * boundary intentionally exposes no other littlefs internals.
 */

#ifndef OPEN_CFW_RUNTIME_LITTLEFS_PAIR_ISSYNC_H
#define OPEN_CFW_RUNTIME_LITTLEFS_PAIR_ISSYNC_H

#include <stdbool.h>
#include <stdint.h>

typedef uint32_t open_cfw_littlefs_pair_issync_block_t;

_Static_assert(
    sizeof(open_cfw_littlefs_pair_issync_block_t) == 4U,
    "littlefs lfs_block_t width changed"
);
_Static_assert(sizeof(bool) == 1U, "reviewed littlefs ABI requires 8-bit bool");

bool open_cfw_littlefs_pair_issync(
    const open_cfw_littlefs_pair_issync_block_t paira[2],
    const open_cfw_littlefs_pair_issync_block_t pairb[2]
);

#endif
