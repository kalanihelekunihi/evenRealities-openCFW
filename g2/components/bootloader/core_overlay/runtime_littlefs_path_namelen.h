/* SPDX-License-Identifier: BSD-3-Clause */
/*
 * The little filesystem
 *
 * Copyright (c) 2022, The littlefs authors.
 * Copyright (c) 2017, Arm Limited. All rights reserved.
 *
 * Production ABI for an adaptation of littlefs v2.10.1
 * lfs_path_namelen(). This bootloader-local leaf calls the already
 * admitted open_cfw_bootloader_strcspn() at its stock entry.
 */

#ifndef OPEN_CFW_BOOTLOADER_RUNTIME_LITTLEFS_PATH_NAMELEN_H
#define OPEN_CFW_BOOTLOADER_RUNTIME_LITTLEFS_PATH_NAMELEN_H

typedef unsigned int open_cfw_bootloader_littlefs_size_t;

open_cfw_bootloader_littlefs_size_t open_cfw_bootloader_littlefs_path_namelen(
    const char *path
);

#endif
