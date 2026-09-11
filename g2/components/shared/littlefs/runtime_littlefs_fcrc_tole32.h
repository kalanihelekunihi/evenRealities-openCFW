/*
 * The little filesystem
 *
 * Copyright (c) 2022, The littlefs authors.
 * Copyright (c) 2017, Arm Limited. All rights reserved.
 * SPDX-License-Identifier: BSD-3-Clause
 *
 * Production ABI for an adaptation of littlefs v2.10.1 lfs_fcrc_tole32().
 * The private upstream struct lfs_fcrc is a 2-word {size, crc} record of
 * uint32_t; this isolated boundary intentionally exposes no other littlefs
 * internals beyond the already admitted lfs_tole32() leaf it calls.
 */

#ifndef OPEN_CFW_RUNTIME_LITTLEFS_FCRC_TOLE32_H
#define OPEN_CFW_RUNTIME_LITTLEFS_FCRC_TOLE32_H

#include <stdint.h>

enum {
    OPEN_CFW_LITTLEFS_FCRC_TOLE32_WORDS = 2
};

_Static_assert(sizeof(uint32_t) == 4U, "littlefs requires 32-bit uint32_t");

/* fcrc[0] is lfs_fcrc.size, fcrc[1] is lfs_fcrc.crc. */
void open_cfw_littlefs_fcrc_tole32(
    uint32_t fcrc[OPEN_CFW_LITTLEFS_FCRC_TOLE32_WORDS]
);

#endif
