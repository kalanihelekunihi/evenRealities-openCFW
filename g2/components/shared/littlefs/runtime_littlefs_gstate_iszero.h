/*
 * The little filesystem
 *
 * Copyright (c) 2022, The littlefs authors.
 * Copyright (c) 2017, Arm Limited. All rights reserved.
 * SPDX-License-Identifier: BSD-3-Clause
 *
 * Production ABI for an adaptation of littlefs v2.10.1 lfs_gstate_iszero().
 * The private upstream lfs_gstate_t is a 3-word {tag, pair[2]} record of
 * uint32_t; this isolated boundary intentionally exposes no other littlefs
 * internals and operates on the raw three-word span exactly as the upstream
 * body does.
 */

#ifndef OPEN_CFW_RUNTIME_LITTLEFS_GSTATE_ISZERO_H
#define OPEN_CFW_RUNTIME_LITTLEFS_GSTATE_ISZERO_H

#include <stdbool.h>
#include <stdint.h>

enum {
    OPEN_CFW_LITTLEFS_GSTATE_ISZERO_WORDS = 3
};

_Static_assert(sizeof(uint32_t) == 4U, "littlefs requires 32-bit uint32_t");
_Static_assert(sizeof(bool) == 1U, "reviewed littlefs ABI requires 8-bit bool");

bool open_cfw_littlefs_gstate_iszero(
    const uint32_t a[OPEN_CFW_LITTLEFS_GSTATE_ISZERO_WORDS]
);

#endif
