/*
 * The little filesystem
 *
 * Copyright (c) 2022, The littlefs authors.
 * Copyright (c) 2017, Arm Limited. All rights reserved.
 * SPDX-License-Identifier: BSD-3-Clause
 *
 * Production ABI for an adaptation of littlefs v2.10.1 lfs_pair_tole32().
 * The private upstream lfs_block_t is exactly uint32_t; this isolated
 * boundary intentionally exposes no other littlefs internals beyond the
 * already admitted lfs_tole32() leaf it calls.
 */

#ifndef OPEN_CFW_RUNTIME_LITTLEFS_PAIR_TOLE32_H
#define OPEN_CFW_RUNTIME_LITTLEFS_PAIR_TOLE32_H

#include <stdint.h>

typedef uint32_t open_cfw_littlefs_pair_tole32_block_t;

_Static_assert(
    sizeof(open_cfw_littlefs_pair_tole32_block_t) == 4U,
    "littlefs lfs_block_t width changed"
);

void open_cfw_littlefs_pair_tole32(
    open_cfw_littlefs_pair_tole32_block_t pair[2]
);

#endif
