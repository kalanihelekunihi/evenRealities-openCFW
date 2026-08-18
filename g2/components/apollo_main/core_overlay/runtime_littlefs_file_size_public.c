/*
 * The little filesystem
 *
 * Copyright (c) 2022, The littlefs authors.
 * Copyright (c) 2017, Arm Limited. All rights reserved.
 * SPDX-License-Identifier: BSD-3-Clause
 *
 * Bounded, freestanding adaptation of the public lfs_file_size() wrapper from
 * littlefs v2.10.1 lfs.c at commit
 * 0494ce7169f06a734a7bd7585f49a9fa91fa7318, tree
 * 06dd0162169d3cb550cd24a3e34d0e4d02983ad3.
 *
 * The official G2 Apollo-main image places this complete public wrapper at
 * [0x004CFC2E, 0x004CFC5C). With the recovered G2 configuration
 * (LFS_THREADSAFE and LFS_YES_TRACE disabled, assertions enabled), the
 * upstream body:
 *
 *     lfs_soff_t lfs_file_size(lfs_t *lfs, lfs_file_t *file) {
 *         int err = LFS_LOCK(lfs->cfg);          // no-op, folds to 0
 *         if (err) { return err; }               // dead
 *         LFS_TRACE(...);                         // no-op
 *         LFS_ASSERT(lfs_mlist_isopen(
 *             lfs->mlist, (struct lfs_mlist*)file));
 *         lfs_soff_t res = lfs_file_size_(lfs, file);
 *         LFS_TRACE(...);                         // no-op
 *         LFS_UNLOCK(lfs->cfg);                   // no-op
 *         return res;
 *     }
 *
 * collapses to the observed sequence: assert the file is open, then tail into
 * the private size body. Both callees are already source-owned leaves and are
 * bound here by symbol (lfs_mlist_isopen at stock 0x004CB082, lfs_file_size_
 * at stock 0x004CE472).
 *
 * Following the reviewed openCFW assertion-seam convention (see the TLSF and
 * FreeRTOS ports), the source does not retain the opaque stock fatal handler
 * at 0x004D09B4 or its vendor build-path/expression literals. The active
 * assertion path instead fails stop locally. The predicate, its evaluation
 * order, and the fall-through to the private body are preserved exactly.
 */

#include "runtime_littlefs_file_size_public.h"

__attribute__((used, noinline))
open_cfw_littlefs_file_size_public_s32
open_cfw_littlefs_file_size_public(
    struct open_cfw_littlefs_file_size_public_lfs *lfs,
    struct open_cfw_littlefs_file_size_public_file *file
)
{
    if (
        open_cfw_littlefs_mlist_isopen(
            lfs->mlist,
            (struct open_cfw_littlefs_file_size_public_node *)file
        ) == 0U
    ) {
        for (;;) {
        }
    }

    return open_cfw_littlefs_file_size_private(lfs, file);
}
