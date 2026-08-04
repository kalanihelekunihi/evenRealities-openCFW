/*
 * The little filesystem
 *
 * Copyright (c) 2022, The littlefs authors.
 * Copyright (c) 2017, Arm Limited. All rights reserved.
 * SPDX-License-Identifier: BSD-3-Clause
 *
 * Altered production adaptation of lfs_tag_chunk() from the authenticated
 * littlefs v2.10.1 source-equivalent baseline at commit
 * 0494ce7169f06a734a7bd7585f49a9fa91fa7318.
 *
 * The official G2 bodies occupy [0x004CAEA0, 0x004CAEA6) in Apollo main and
 * [0x00410BA8, 0x00410BAE) in the bootloader. This pure scalar leaf has no
 * provider, global state, allocation, or hardware path.
 */

#include "runtime_littlefs_tag_chunk.h"

__attribute__((used, noinline))
uint8_t open_cfw_littlefs_tag_chunk(open_cfw_littlefs_tag_t tag)
{
    return (uint8_t)((tag & UINT32_C(0x0ff00000)) >> 20U);
}
