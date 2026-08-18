/*
 * The little filesystem — SPDX-License-Identifier: BSD-3-Clause
 *
 * Recovered ABI for the G2 lfs_file_size() public wrapper. The mlist pointer
 * sits at offset 0x28 of the recovered G2 lfs_t (the stock wrapper at
 * 0x004CFC2E loads `ldr r0, [lfs, #0x28]`). Both callees are already
 * source-owned overlay leaves, bound here by symbol.
 */
#ifndef OPEN_CFW_LITTLEFS_FILE_SIZE_PUBLIC_H
#define OPEN_CFW_LITTLEFS_FILE_SIZE_PUBLIC_H

typedef __INT32_TYPE__ open_cfw_littlefs_file_size_public_s32;

struct open_cfw_littlefs_file_size_public_node;
struct open_cfw_littlefs_file_size_public_file;

struct open_cfw_littlefs_file_size_public_lfs {
    unsigned char open_cfw_reserved_before_mlist[0x28];
    struct open_cfw_littlefs_file_size_public_node *mlist;
};

extern int open_cfw_littlefs_mlist_isopen(
    struct open_cfw_littlefs_file_size_public_node *mlist,
    struct open_cfw_littlefs_file_size_public_node *item);

extern open_cfw_littlefs_file_size_public_s32 open_cfw_littlefs_file_size_private(
    struct open_cfw_littlefs_file_size_public_lfs *lfs,
    struct open_cfw_littlefs_file_size_public_file *file);

#endif
