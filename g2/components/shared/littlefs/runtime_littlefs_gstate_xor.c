/*
 * The little filesystem
 *
 * Copyright (c) 2022, The littlefs authors.
 * Copyright (c) 2017, Arm Limited. All rights reserved.
 * SPDX-License-Identifier: BSD-3-Clause
 *
 * Production adaptation of lfs_gstate_xor() from the authenticated littlefs
 * v2.10.1 source-equivalent baseline at commit
 * 0494ce7169f06a734a7bd7585f49a9fa91fa7318.
 *
 * The official G2 bootloader body occupies [0x00410BDC, 0x00410BFA). This
 * pure scalar leaf has no provider, global state, allocation, or hardware
 * path.
 */

#include "runtime_littlefs_gstate_xor.h"

__attribute__((used, noinline))
void open_cfw_littlefs_gstate_xor(
    uint32_t a[OPEN_CFW_LITTLEFS_GSTATE_XOR_WORDS],
    const uint32_t b[OPEN_CFW_LITTLEFS_GSTATE_XOR_WORDS])
{
    for (int i = 0; i < OPEN_CFW_LITTLEFS_GSTATE_XOR_WORDS; i++) {
        a[i] ^= b[i];
    }
}
