/* SPDX-License-Identifier: BSD-3-Clause */
/*
 * The little filesystem
 *
 * Copyright (c) 2022, The littlefs authors.
 * Copyright (c) 2017, Arm Limited. All rights reserved.
 *
 * Production ABI for an adaptation of littlefs v2.10.1 lfs_cache_zero().
 * The recovered lfs_t ABI places the lfs_config pointer at offset 0x68 and
 * lfs_config.cache_size at offset 0x28 within it; this leaf calls the
 * already admitted open_cfw_bootloader_aeabi_memset() at its stock entry.
 */

#ifndef OPEN_CFW_BOOTLOADER_RUNTIME_LITTLEFS_CACHE_ZERO_H
#define OPEN_CFW_BOOTLOADER_RUNTIME_LITTLEFS_CACHE_ZERO_H

typedef unsigned int open_cfw_bootloader_littlefs_cache_zero_u32;
typedef unsigned char open_cfw_bootloader_littlefs_cache_zero_u8;

struct open_cfw_bootloader_littlefs_cache_zero_cache {
    open_cfw_bootloader_littlefs_cache_zero_u32 block;
    open_cfw_bootloader_littlefs_cache_zero_u32 off;
    open_cfw_bootloader_littlefs_cache_zero_u32 size;
    open_cfw_bootloader_littlefs_cache_zero_u8 *buffer;
};

/* Only the fields up to and including cache_size are named; later fields
 * are represented as padding since this leaf never dereferences them. */
struct open_cfw_bootloader_littlefs_cache_zero_config {
    open_cfw_bootloader_littlefs_cache_zero_u8 padding_before_cache_size[0x28];
    open_cfw_bootloader_littlefs_cache_zero_u32 cache_size;
};

/* Only the field at the recovered cfg offset (0x68) is named; earlier
 * fields are represented as padding since this leaf never dereferences
 * them. */
struct open_cfw_bootloader_littlefs_cache_zero_lfs {
    open_cfw_bootloader_littlefs_cache_zero_u8 padding_before_cfg[0x68];
    const struct open_cfw_bootloader_littlefs_cache_zero_config *cfg;
};

_Static_assert(
    __builtin_offsetof(
        struct open_cfw_bootloader_littlefs_cache_zero_config,
        cache_size
    ) == 0x28U,
    "littlefs lfs_config cache_size offset changed"
);
_Static_assert(
    __builtin_offsetof(
        struct open_cfw_bootloader_littlefs_cache_zero_lfs,
        cfg
    ) == 0x68U,
    "littlefs lfs_t cfg offset changed"
);
_Static_assert(
    __builtin_offsetof(
        struct open_cfw_bootloader_littlefs_cache_zero_cache,
        buffer
    ) == 0x0CU,
    "littlefs lfs_cache_t buffer offset changed"
);

void open_cfw_bootloader_littlefs_cache_zero(
    const struct open_cfw_bootloader_littlefs_cache_zero_lfs *lfs,
    struct open_cfw_bootloader_littlefs_cache_zero_cache *pcache
);

#endif
