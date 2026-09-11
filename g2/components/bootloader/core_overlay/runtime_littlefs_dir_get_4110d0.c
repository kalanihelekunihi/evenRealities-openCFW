/*
 * The little filesystem
 *
 * Copyright (c) 2022, The littlefs authors.
 * Copyright (c) 2017, Arm Limited. All rights reserved.
 * SPDX-License-Identifier: BSD-3-Clause
 *
 * Bounded, freestanding port of lfs_dir_get() from littlefs v2.10.1 lfs.c at
 * commit 0494ce7169f06a734a7bd7585f49a9fa91fa7318:
 *
 *   static lfs_stag_t lfs_dir_get(lfs_t *lfs, const lfs_mdir_t *dir,
 *           lfs_tag_t gmask, lfs_tag_t gtag, void *buffer) {
 *       return lfs_dir_getslice(lfs, dir,
 *               gmask, gtag,
 *               0, buffer, lfs_tag_size(gtag));
 *   }
 *
 * The official G2 bootloader contains this complete private leaf at
 * [0x004110D0, 0x004110F8). It owns no pointers, configuration, callbacks,
 * storage operations, or hardware state of its own: it forwards its five
 * arguments to lfs_dir_getslice() at the retained entry 0x00410F42 (a
 * separate, as-yet-unclassified bootloader closure), together with a
 * literal zero byte offset and the size lfs_tag_size() computes for gtag
 * at the already source-owned redirect entry 0x00410BC0.
 */

typedef __UINT32_TYPE__ open_cfw_littlefs_dir_get_u32;
typedef __INT32_TYPE__ open_cfw_littlefs_dir_get_i32;

_Static_assert(sizeof(open_cfw_littlefs_dir_get_u32) == 4U,
    "littlefs uint32_t width changed");
_Static_assert(sizeof(open_cfw_littlefs_dir_get_i32) == 4U,
    "littlefs int32_t width changed");

#if defined(OPEN_CFW_LITTLEFS_DIR_GET_HOST)
open_cfw_littlefs_dir_get_u32 open_cfw_littlefs_dir_get_host_tag_size(
    open_cfw_littlefs_dir_get_u32 tag);
open_cfw_littlefs_dir_get_i32 open_cfw_littlefs_dir_get_host_getslice(
    void *lfs, const void *dir,
    open_cfw_littlefs_dir_get_u32 gmask, open_cfw_littlefs_dir_get_u32 gtag,
    open_cfw_littlefs_dir_get_u32 goff, void *gbuffer,
    open_cfw_littlefs_dir_get_u32 gsize);
#else
/* Already source-owned shared leaf; matches
 * components/shared/littlefs/runtime_littlefs_tag_size.h exactly. */
extern open_cfw_littlefs_dir_get_u32 open_cfw_littlefs_tag_size(
    open_cfw_littlefs_dir_get_u32 tag);
/* Still-retained bootloader entry at 0x00410F42; a separate,
 * as-yet-unclassified closure. */
extern open_cfw_littlefs_dir_get_i32 lfs_dir_getslice(
    void *lfs, const void *dir,
    open_cfw_littlefs_dir_get_u32 gmask, open_cfw_littlefs_dir_get_u32 gtag,
    open_cfw_littlefs_dir_get_u32 goff, void *gbuffer,
    open_cfw_littlefs_dir_get_u32 gsize);
#endif

__attribute__((used, noinline))
open_cfw_littlefs_dir_get_i32
open_cfw_bootloader_lfs_dir_get_4110d0(
    void *lfs, const void *dir,
    open_cfw_littlefs_dir_get_u32 gmask, open_cfw_littlefs_dir_get_u32 gtag,
    void *buffer)
{
#if defined(OPEN_CFW_LITTLEFS_DIR_GET_HOST)
    return open_cfw_littlefs_dir_get_host_getslice(lfs, dir, gmask, gtag, 0,
        buffer, open_cfw_littlefs_dir_get_host_tag_size(gtag));
#else
    return lfs_dir_getslice(lfs, dir, gmask, gtag, 0, buffer,
        open_cfw_littlefs_tag_size(gtag));
#endif
}
