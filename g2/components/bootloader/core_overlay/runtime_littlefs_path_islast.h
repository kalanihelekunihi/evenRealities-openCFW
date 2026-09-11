/* SPDX-License-Identifier: BSD-3-Clause */
/*
 * The little filesystem
 *
 * Copyright (c) 2022, The littlefs authors.
 * Copyright (c) 2017, Arm Limited. All rights reserved.
 *
 * Production ABI for an adaptation of littlefs v2.10.1 lfs_path_islast().
 * This bootloader-local leaf calls the sibling
 * open_cfw_bootloader_littlefs_path_namelen() and the already admitted
 * open_cfw_bootloader_strspn() at their stock entries.
 */

#ifndef OPEN_CFW_BOOTLOADER_RUNTIME_LITTLEFS_PATH_ISLAST_H
#define OPEN_CFW_BOOTLOADER_RUNTIME_LITTLEFS_PATH_ISLAST_H

#include <stdbool.h>

bool open_cfw_bootloader_littlefs_path_islast(const char *path);

#endif
