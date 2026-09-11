/*
 * The little filesystem
 *
 * Copyright (c) 2022, The littlefs authors.
 * Copyright (c) 2017, Arm Limited. All rights reserved.
 * SPDX-License-Identifier: BSD-3-Clause
 *
 * Production adaptation of lfs_superblock_tole32() from the authenticated
 * littlefs v2.10.1 source-equivalent baseline at commit
 * 0494ce7169f06a734a7bd7585f49a9fa91fa7318.
 *
 * The official G2 bootloader body occupies [0x00410D54, 0x00410D8A). It
 * calls the already admitted lfs_tole32() leaf (open_cfw_littlefs_util
 * quartet, "components/apollo_main/core_overlay/runtime_littlefs_util_endian.c")
 * at its stock entry, once per word. This leaf owns no provider, global
 * state, allocation, or hardware path.
 */

#include "runtime_littlefs_superblock_tole32.h"

extern unsigned int open_cfw_littlefs_util_tole32(unsigned int a);

__attribute__((used, noinline))
void open_cfw_littlefs_superblock_tole32(
    uint32_t superblock[OPEN_CFW_LITTLEFS_SUPERBLOCK_TOLE32_WORDS])
{
    superblock[0] = open_cfw_littlefs_util_tole32(superblock[0]);
    superblock[1] = open_cfw_littlefs_util_tole32(superblock[1]);
    superblock[2] = open_cfw_littlefs_util_tole32(superblock[2]);
    superblock[3] = open_cfw_littlefs_util_tole32(superblock[3]);
    superblock[4] = open_cfw_littlefs_util_tole32(superblock[4]);
    superblock[5] = open_cfw_littlefs_util_tole32(superblock[5]);
}
