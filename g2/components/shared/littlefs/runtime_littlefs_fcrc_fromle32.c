/*
 * The little filesystem
 *
 * Copyright (c) 2022, The littlefs authors.
 * Copyright (c) 2017, Arm Limited. All rights reserved.
 * SPDX-License-Identifier: BSD-3-Clause
 *
 * Production adaptation of lfs_fcrc_fromle32() from the authenticated
 * littlefs v2.10.1 source-equivalent baseline at commit
 * 0494ce7169f06a734a7bd7585f49a9fa91fa7318.
 *
 * The official G2 bootloader body occupies [0x00410CC6, 0x00410CDC). It
 * calls the already admitted lfs_fromle32() leaf (open_cfw_littlefs_util
 * quartet, "components/apollo_main/core_overlay/runtime_littlefs_util_endian.c")
 * at its stock entry, once per word. This leaf owns no provider, global
 * state, allocation, or hardware path.
 */

#include "runtime_littlefs_fcrc_fromle32.h"

extern unsigned int open_cfw_littlefs_util_fromle32(unsigned int a);

__attribute__((used, noinline))
void open_cfw_littlefs_fcrc_fromle32(
    uint32_t fcrc[OPEN_CFW_LITTLEFS_FCRC_FROMLE32_WORDS])
{
    fcrc[0] = open_cfw_littlefs_util_fromle32(fcrc[0]);
    fcrc[1] = open_cfw_littlefs_util_fromle32(fcrc[1]);
}
