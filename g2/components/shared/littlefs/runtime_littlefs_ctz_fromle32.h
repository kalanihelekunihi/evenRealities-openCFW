/*
 * The little filesystem
 *
 * Copyright (c) 2022, The littlefs authors.
 * Copyright (c) 2017, Arm Limited. All rights reserved.
 * SPDX-License-Identifier: BSD-3-Clause
 *
 * Production ABI for an adaptation of littlefs v2.10.1 lfs_ctz_fromle32().
 * The private upstream struct lfs_ctz is a 2-word {head, size} record of
 * uint32_t; this isolated boundary intentionally exposes no other littlefs
 * internals beyond the already admitted lfs_fromle32() leaf it calls.
 */

#ifndef OPEN_CFW_RUNTIME_LITTLEFS_CTZ_FROMLE32_H
#define OPEN_CFW_RUNTIME_LITTLEFS_CTZ_FROMLE32_H

#include <stdint.h>

enum {
    OPEN_CFW_LITTLEFS_CTZ_FROMLE32_WORDS = 2
};

_Static_assert(sizeof(uint32_t) == 4U, "littlefs requires 32-bit uint32_t");

/* ctz[0] is lfs_ctz.head, ctz[1] is lfs_ctz.size. */
void open_cfw_littlefs_ctz_fromle32(
    uint32_t ctz[OPEN_CFW_LITTLEFS_CTZ_FROMLE32_WORDS]
);

#endif
