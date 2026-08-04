/*
 * The little filesystem
 *
 * Copyright (c) 2022, The littlefs authors.
 * Copyright (c) 2017, Arm Limited. All rights reserved.
 * SPDX-License-Identifier: BSD-3-Clause
 *
 * Bounded, freestanding port of lfs_alloc_ckpoint() from littlefs v2.10.1
 * lfs.c at commit 0494ce7169f06a734a7bd7585f49a9fa91fa7318.
 *
 * The official G2 images contain the same complete private leaf at
 * Apollo-main [0x004CB0E0, 0x004CB0E6) and bootloader
 * [0x00410DE8, 0x00410DEE). It copies lfs_t.block_count at offset 0x6c to
 * lfs_t.lookahead.ckpoint at offset 0x60. There are no calls, branches,
 * literals, relocations, configuration dereferences, block callbacks, or
 * MSPI dependencies.
 */

typedef unsigned int open_cfw_littlefs_alloc_ckpoint_u32;
typedef unsigned char open_cfw_littlefs_alloc_ckpoint_u8;

struct open_cfw_littlefs_alloc_ckpoint_cache {
    open_cfw_littlefs_alloc_ckpoint_u32 block;
    open_cfw_littlefs_alloc_ckpoint_u32 offset;
    open_cfw_littlefs_alloc_ckpoint_u32 size;
    open_cfw_littlefs_alloc_ckpoint_u8 *buffer;
};

struct open_cfw_littlefs_alloc_ckpoint_gstate {
    open_cfw_littlefs_alloc_ckpoint_u32 tag;
    open_cfw_littlefs_alloc_ckpoint_u32 pair[2];
};

struct open_cfw_littlefs_alloc_ckpoint_mlist;
struct open_cfw_littlefs_alloc_ckpoint_config;

struct open_cfw_littlefs_alloc_ckpoint_lookahead {
    open_cfw_littlefs_alloc_ckpoint_u32 start;
    open_cfw_littlefs_alloc_ckpoint_u32 size;
    open_cfw_littlefs_alloc_ckpoint_u32 next;
    open_cfw_littlefs_alloc_ckpoint_u32 checkpoint;
    open_cfw_littlefs_alloc_ckpoint_u8 *buffer;
};

struct open_cfw_littlefs_alloc_ckpoint_lfs {
    struct open_cfw_littlefs_alloc_ckpoint_cache read_cache;
    struct open_cfw_littlefs_alloc_ckpoint_cache program_cache;

    open_cfw_littlefs_alloc_ckpoint_u32 root[2];
    struct open_cfw_littlefs_alloc_ckpoint_mlist *open_list;
    open_cfw_littlefs_alloc_ckpoint_u32 seed;

    struct open_cfw_littlefs_alloc_ckpoint_gstate global_state;
    struct open_cfw_littlefs_alloc_ckpoint_gstate disk_state;
    struct open_cfw_littlefs_alloc_ckpoint_gstate delta_state;

    struct open_cfw_littlefs_alloc_ckpoint_lookahead lookahead;

    const struct open_cfw_littlefs_alloc_ckpoint_config *configuration;
    open_cfw_littlefs_alloc_ckpoint_u32 block_count;
    open_cfw_littlefs_alloc_ckpoint_u32 name_max;
    open_cfw_littlefs_alloc_ckpoint_u32 file_max;
    open_cfw_littlefs_alloc_ckpoint_u32 attribute_max;
    open_cfw_littlefs_alloc_ckpoint_u32 inline_max;
};

#if defined(__arm__)
_Static_assert(sizeof(void *) == 4U, "Apollo510 requires 32-bit pointers");
_Static_assert(
    sizeof(open_cfw_littlefs_alloc_ckpoint_u32) == 4U,
    "littlefs 32-bit scalar width changed"
);
_Static_assert(
    sizeof(struct open_cfw_littlefs_alloc_ckpoint_cache) == 0x10U,
    "littlefs lfs_cache_t ABI changed"
);
_Static_assert(
    sizeof(struct open_cfw_littlefs_alloc_ckpoint_gstate) == 0x0CU,
    "littlefs lfs_gstate_t ABI changed"
);
_Static_assert(
    sizeof(struct open_cfw_littlefs_alloc_ckpoint_lookahead) == 0x14U,
    "littlefs lfs_lookahead ABI changed"
);
_Static_assert(
    sizeof(struct open_cfw_littlefs_alloc_ckpoint_lfs) == 0x80U,
    "littlefs lfs_t ABI changed"
);
_Static_assert(
    __builtin_offsetof(
        struct open_cfw_littlefs_alloc_ckpoint_lfs,
        lookahead
    ) == 0x54U,
    "littlefs lfs_t lookahead offset changed"
);
_Static_assert(
    __builtin_offsetof(
        struct open_cfw_littlefs_alloc_ckpoint_lfs,
        lookahead
    ) +
        __builtin_offsetof(
            struct open_cfw_littlefs_alloc_ckpoint_lookahead,
            checkpoint
        ) == 0x60U,
    "littlefs lookahead checkpoint offset changed"
);
_Static_assert(
    __builtin_offsetof(
        struct open_cfw_littlefs_alloc_ckpoint_lfs,
        block_count
    ) == 0x6CU,
    "littlefs lfs_t block-count offset changed"
);
#endif

__attribute__((used, noinline))
void open_cfw_littlefs_alloc_ckpoint(
    struct open_cfw_littlefs_alloc_ckpoint_lfs *lfs
)
{
    lfs->lookahead.checkpoint = lfs->block_count;
}
