/*
 * The little filesystem
 *
 * Copyright (c) 2022, The littlefs authors.
 * Copyright (c) 2017, Arm Limited. All rights reserved.
 * SPDX-License-Identifier: BSD-3-Clause
 *
 * Production ABI for an adaptation of littlefs v2.10.1
 * lfs_superblock_tole32(). The private upstream lfs_superblock_t is a
 * 6-word {version, block_size, block_count, name_max, file_max, attr_max}
 * record of uint32_t; this isolated boundary intentionally exposes no other
 * littlefs internals beyond the already admitted lfs_tole32() leaf it
 * calls.
 */

#ifndef OPEN_CFW_RUNTIME_LITTLEFS_SUPERBLOCK_TOLE32_H
#define OPEN_CFW_RUNTIME_LITTLEFS_SUPERBLOCK_TOLE32_H

#include <stdint.h>

enum {
    OPEN_CFW_LITTLEFS_SUPERBLOCK_TOLE32_WORDS = 6
};

_Static_assert(sizeof(uint32_t) == 4U, "littlefs requires 32-bit uint32_t");

/* superblock[0..5] is {version, block_size, block_count, name_max,
 * file_max, attr_max}. */
void open_cfw_littlefs_superblock_tole32(
    uint32_t superblock[OPEN_CFW_LITTLEFS_SUPERBLOCK_TOLE32_WORDS]
);

#endif
