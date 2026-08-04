/*
 * The little filesystem
 *
 * Copyright (c) 2022, The littlefs authors.
 * Copyright (c) 2017, Arm Limited. All rights reserved.
 * SPDX-License-Identifier: BSD-3-Clause
 *
 * Isolated G2 ABI for an altered adaptation of littlefs v2.10.1
 * lfs_file_rewind_(). The private filesystem and file types stay opaque
 * because this boundary only forwards them to lfs_file_seek_().
 */

#ifndef OPEN_CFW_RUNTIME_LITTLEFS_FILE_REWIND_PRIVATE_H
#define OPEN_CFW_RUNTIME_LITTLEFS_FILE_REWIND_PRIVATE_H

typedef __INT32_TYPE__ open_cfw_littlefs_file_rewind_private_soff;

struct open_cfw_littlefs_file_rewind_private_lfs;
struct open_cfw_littlefs_file_rewind_private_file;

enum {
    OPEN_CFW_LITTLEFS_FILE_REWIND_PRIVATE_SEEK_SET = 0,
    OPEN_CFW_LITTLEFS_FILE_REWIND_PRIVATE_SEEK_ADDRESS = 0x004CE3BCU
};

_Static_assert(sizeof(int) == 4U, "Apollo510 requires 32-bit int");
_Static_assert(
    sizeof(open_cfw_littlefs_file_rewind_private_soff) == 4U,
    "littlefs lfs_soff_t width changed"
);
_Static_assert(
    OPEN_CFW_LITTLEFS_FILE_REWIND_PRIVATE_SEEK_SET == 0,
    "littlefs LFS_SEEK_SET value changed"
);

#if defined(__arm__)
_Static_assert(sizeof(void *) == 4U, "Apollo510 requires 32-bit pointers");
#endif

/* Production binding to the retained private lfs_file_seek_ at 0x004CE3BC. */
open_cfw_littlefs_file_rewind_private_soff
open_cfw_littlefs_file_seek_private(
    struct open_cfw_littlefs_file_rewind_private_lfs *lfs,
    struct open_cfw_littlefs_file_rewind_private_file *file,
    open_cfw_littlefs_file_rewind_private_soff offset,
    int whence
);

int open_cfw_littlefs_file_rewind_private(
    struct open_cfw_littlefs_file_rewind_private_lfs *lfs,
    struct open_cfw_littlefs_file_rewind_private_file *file
);

#endif
