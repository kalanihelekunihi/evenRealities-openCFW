/*
 * The little filesystem
 *
 * Copyright (c) 2022, The littlefs authors.
 * Copyright (c) 2017, Arm Limited. All rights reserved.
 * SPDX-License-Identifier: BSD-3-Clause
 *
 * Production ABI for an adaptation of littlefs v2.10.1
 * lfs_gstate_hasmovehere(). The private upstream lfs_gstate_t is a 3-word
 * {tag, pair[2]} record of uint32_t; this isolated boundary intentionally
 * exposes no other littlefs internals beyond the already admitted
 * lfs_tag_type1() leaf and the sibling lfs_pair_cmp() leaf it calls.
 */

#ifndef OPEN_CFW_RUNTIME_LITTLEFS_GSTATE_HASMOVEHERE_H
#define OPEN_CFW_RUNTIME_LITTLEFS_GSTATE_HASMOVEHERE_H

#include <stdbool.h>
#include <stdint.h>

_Static_assert(sizeof(uint32_t) == 4U, "littlefs requires 32-bit uint32_t");
_Static_assert(sizeof(bool) == 1U, "reviewed littlefs ABI requires 8-bit bool");

/* gstate points at the 3-word {tag, pair[2]} record; gstate[0] is the tag
 * and gstate[1..2] is its own pair, unused by this leaf. */
bool open_cfw_littlefs_gstate_hasmovehere(
    const uint32_t gstate[3],
    const uint32_t pair[2]
);

#endif
