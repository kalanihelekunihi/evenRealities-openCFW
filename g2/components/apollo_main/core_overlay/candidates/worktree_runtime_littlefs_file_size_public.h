/*
 * SPDX-License-Identifier: BSD-3-Clause
 *
 * Isolated G2 ABI for the public littlefs v2.10.1 lfs_file_size() wrapper.
 * The wrapper only needs the open-file membership list head (lfs->mlist) and
 * the file's leading intrusive-list node, so just those fields are reproduced
 * here. The private body lfs_file_size_() and the lfs_mlist_isopen() predicate
 * are already source-owned leaves; this boundary binds to them by symbol and
 * inherits no unrelated littlefs configuration.
 */

#ifndef OPEN_CFW_RUNTIME_LITTLEFS_FILE_SIZE_PUBLIC_H
#define OPEN_CFW_RUNTIME_LITTLEFS_FILE_SIZE_PUBLIC_H

typedef __UINT32_TYPE__ open_cfw_littlefs_file_size_public_u32;
typedef __INT32_TYPE__ open_cfw_littlefs_file_size_public_s32;
typedef __UINT8_TYPE__ open_cfw_littlefs_file_size_public_u8;

/*
 * The intrusive metadata-list node. Both struct lfs_mlist and struct lfs_file
 * start with this same self-referential next pointer, so lfs_mlist_isopen walks
 * the list purely through offset 0.
 */
struct open_cfw_littlefs_file_size_public_node {
    struct open_cfw_littlefs_file_size_public_node *next;
};

struct open_cfw_littlefs_file_size_public_cache {
    open_cfw_littlefs_file_size_public_u32 block;
    open_cfw_littlefs_file_size_public_u32 offset;
    open_cfw_littlefs_file_size_public_u32 size;
    open_cfw_littlefs_file_size_public_u8 *buffer;
};

/*
 * lfs_t prefix through lfs->mlist. The recovered wrapper loads the membership
 * list head from lfs+0x28 (rcache 0x10, pcache 0x10, root[2] 0x08).
 */
struct open_cfw_littlefs_file_size_public_lfs {
    struct open_cfw_littlefs_file_size_public_cache rcache;
    struct open_cfw_littlefs_file_size_public_cache pcache;
    open_cfw_littlefs_file_size_public_u32 root[2];
    struct open_cfw_littlefs_file_size_public_node *mlist;
};

/* The concrete lfs_file_t layout is owned by the private size leaf. */
struct open_cfw_littlefs_file_size_public_file;

_Static_assert(
    sizeof(open_cfw_littlefs_file_size_public_u32) == 4U,
    "littlefs lfs_size_t width changed"
);
_Static_assert(
    sizeof(open_cfw_littlefs_file_size_public_s32) == 4U,
    "littlefs lfs_soff_t width changed"
);
_Static_assert(
    __builtin_offsetof(
        struct open_cfw_littlefs_file_size_public_node,
        next
    ) == 0U,
    "littlefs mlist next offset changed"
);

#if defined(__arm__)
_Static_assert(sizeof(void *) == 4U, "Apollo510 requires 32-bit pointers");
_Static_assert(
    sizeof(struct open_cfw_littlefs_file_size_public_cache) == 0x10U,
    "littlefs lfs_cache_t ABI changed"
);
_Static_assert(
    __builtin_offsetof(
        struct open_cfw_littlefs_file_size_public_lfs,
        mlist
    ) == 0x28U,
    "littlefs lfs_t mlist offset changed"
);
#endif

/*
 * Source-owned open-file membership predicate; stock private leaf at
 * 0x004CB082. Returns the recovered 32-bit 0/1 result.
 */
open_cfw_littlefs_file_size_public_u32 open_cfw_littlefs_mlist_isopen(
    struct open_cfw_littlefs_file_size_public_node *head,
    struct open_cfw_littlefs_file_size_public_node *node
);

/*
 * Source-owned private size body; stock private leaf at 0x004CE472.
 */
open_cfw_littlefs_file_size_public_s32 open_cfw_littlefs_file_size_private(
    struct open_cfw_littlefs_file_size_public_lfs *lfs,
    struct open_cfw_littlefs_file_size_public_file *file
);

open_cfw_littlefs_file_size_public_s32 open_cfw_littlefs_file_size_public(
    struct open_cfw_littlefs_file_size_public_lfs *lfs,
    struct open_cfw_littlefs_file_size_public_file *file
);

#endif
