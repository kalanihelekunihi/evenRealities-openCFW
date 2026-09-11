/*
 * The little filesystem
 *
 * Copyright (c) 2022, The littlefs authors.
 * Copyright (c) 2017, Arm Limited. All rights reserved.
 * SPDX-License-Identifier: BSD-3-Clause
 *
 * Production ABI for an adaptation of littlefs v2.10.1
 * lfs_gstate_needssuperblock(). The private upstream lfs_gstate_t begins
 * with a uint32_t tag field; this isolated boundary intentionally exposes
 * no other littlefs internals beyond the already admitted lfs_tag_size()
 * leaf it calls.
 */

#ifndef OPEN_CFW_RUNTIME_LITTLEFS_GSTATE_NEEDSSUPERBLOCK_H
#define OPEN_CFW_RUNTIME_LITTLEFS_GSTATE_NEEDSSUPERBLOCK_H

#include <stdbool.h>
#include <stdint.h>

_Static_assert(sizeof(uint32_t) == 4U, "littlefs requires 32-bit uint32_t");
_Static_assert(sizeof(bool) == 1U, "reviewed littlefs ABI requires 8-bit bool");

bool open_cfw_littlefs_gstate_needssuperblock(const uint32_t *gstate_tag);

#endif
