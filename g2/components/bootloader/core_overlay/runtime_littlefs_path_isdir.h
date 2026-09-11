/* SPDX-License-Identifier: BSD-3-Clause */
/*
 * The little filesystem
 *
 * Copyright (c) 2022, The littlefs authors.
 * Copyright (c) 2017, Arm Limited. All rights reserved.
 *
 * Production ABI for an adaptation of littlefs v2.10.1 lfs_path_isdir().
 * This bootloader-local leaf calls the sibling
 * open_cfw_bootloader_littlefs_path_namelen() at its stock entry.
 */

#ifndef OPEN_CFW_BOOTLOADER_RUNTIME_LITTLEFS_PATH_ISDIR_H
#define OPEN_CFW_BOOTLOADER_RUNTIME_LITTLEFS_PATH_ISDIR_H

#include <stdbool.h>

bool open_cfw_bootloader_littlefs_path_isdir(const char *path);

#endif
