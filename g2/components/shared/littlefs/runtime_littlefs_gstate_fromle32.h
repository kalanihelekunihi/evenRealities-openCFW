/*
 * The little filesystem
 *
 * Copyright (c) 2022, The littlefs authors.
 * Copyright (c) 2017, Arm Limited. All rights reserved.
 * SPDX-License-Identifier: BSD-3-Clause
 *
 * Production ABI for an adaptation of littlefs v2.10.1
 * lfs_gstate_fromle32(). The private upstream lfs_gstate_t is a 3-word
 * {tag, pair[2]} record of uint32_t; this isolated boundary intentionally
 * exposes no other littlefs internals beyond the already admitted
 * lfs_fromle32() leaf it calls.
 */

#ifndef OPEN_CFW_RUNTIME_LITTLEFS_GSTATE_FROMLE32_H
#define OPEN_CFW_RUNTIME_LITTLEFS_GSTATE_FROMLE32_H

#include <stdint.h>

enum {
    OPEN_CFW_LITTLEFS_GSTATE_FROMLE32_WORDS = 3
};

_Static_assert(sizeof(uint32_t) == 4U, "littlefs requires 32-bit uint32_t");

void open_cfw_littlefs_gstate_fromle32(
    uint32_t gstate[OPEN_CFW_LITTLEFS_GSTATE_FROMLE32_WORDS]
);

#endif
