/*
 * The little filesystem
 *
 * Copyright (c) 2022, The littlefs authors.
 * Copyright (c) 2017, Arm Limited. All rights reserved.
 * SPDX-License-Identifier: BSD-3-Clause
 *
 * Bounded, freestanding source replacement for lfs_alloc_lookahead() from
 * littlefs v2.10.1 lfs.c at commit
 * 0494ce7169f06a734a7bd7585f49a9fa91fa7318, tree
 * 06dd0162169d3cb550cd24a3e34d0e4d02983ad3.
 *
 * Both official G2 images retain the same complete private callback at
 * Apollo-main [0x004CB0F6, 0x004CB12E) and bootloader
 * [0x00410DFE, 0x00410E36). The source-visible compatibility boundary is
 * limited to four authenticated lfs_t fields:
 *
 *   lookahead.start   +0x54
 *   lookahead.size    +0x58
 *   lookahead.buffer  +0x64
 *   block_count       +0x6c
 *
 * The callback does not call another littlefs function, dereference the
 * configuration pointer, allocate, or access the block device. Its two
 * official consumers store the callback's Thumb entry in lfs_alloc_scan.
 */

typedef unsigned char open_cfw_littlefs_alloc_lookahead_u8;
typedef unsigned int open_cfw_littlefs_alloc_lookahead_u32;

struct open_cfw_littlefs_alloc_lookahead_cache {
    open_cfw_littlefs_alloc_lookahead_u32 block;
    open_cfw_littlefs_alloc_lookahead_u32 offset;
    open_cfw_littlefs_alloc_lookahead_u32 size;
    open_cfw_littlefs_alloc_lookahead_u8 *buffer;
};

struct open_cfw_littlefs_alloc_lookahead_gstate {
    open_cfw_littlefs_alloc_lookahead_u32 tag;
    open_cfw_littlefs_alloc_lookahead_u32 pair[2];
};

struct open_cfw_littlefs_alloc_lookahead_mlist;
struct open_cfw_littlefs_alloc_lookahead_config;

struct open_cfw_littlefs_alloc_lookahead_state {
    open_cfw_littlefs_alloc_lookahead_u32 start;
    open_cfw_littlefs_alloc_lookahead_u32 size;
    open_cfw_littlefs_alloc_lookahead_u32 next;
    open_cfw_littlefs_alloc_lookahead_u32 checkpoint;
    open_cfw_littlefs_alloc_lookahead_u8 *buffer;
};

struct open_cfw_littlefs_alloc_lookahead_lfs {
    struct open_cfw_littlefs_alloc_lookahead_cache read_cache;
    struct open_cfw_littlefs_alloc_lookahead_cache program_cache;

    open_cfw_littlefs_alloc_lookahead_u32 root[2];
    struct open_cfw_littlefs_alloc_lookahead_mlist *open_list;
    open_cfw_littlefs_alloc_lookahead_u32 seed;

    struct open_cfw_littlefs_alloc_lookahead_gstate global_state;
    struct open_cfw_littlefs_alloc_lookahead_gstate disk_state;
    struct open_cfw_littlefs_alloc_lookahead_gstate delta_state;

    struct open_cfw_littlefs_alloc_lookahead_state lookahead;

    const struct open_cfw_littlefs_alloc_lookahead_config *configuration;
    open_cfw_littlefs_alloc_lookahead_u32 block_count;
    open_cfw_littlefs_alloc_lookahead_u32 name_max;
    open_cfw_littlefs_alloc_lookahead_u32 file_max;
    open_cfw_littlefs_alloc_lookahead_u32 attribute_max;
    open_cfw_littlefs_alloc_lookahead_u32 inline_max;
};

#if defined(__arm__)
_Static_assert(sizeof(void *) == 4U, "Apollo510 requires 32-bit pointers");
_Static_assert(
    sizeof(open_cfw_littlefs_alloc_lookahead_u32) == 4U,
    "littlefs 32-bit scalar width changed"
);
_Static_assert(sizeof(int) == 4U, "littlefs callback result ABI changed");
_Static_assert(
    sizeof(struct open_cfw_littlefs_alloc_lookahead_cache) == 0x10U,
    "littlefs lfs_cache_t ABI changed"
);
_Static_assert(
    sizeof(struct open_cfw_littlefs_alloc_lookahead_gstate) == 0x0CU,
    "littlefs lfs_gstate_t ABI changed"
);
_Static_assert(
    sizeof(struct open_cfw_littlefs_alloc_lookahead_state) == 0x14U,
    "littlefs lfs_lookahead ABI changed"
);
_Static_assert(
    sizeof(struct open_cfw_littlefs_alloc_lookahead_lfs) == 0x80U,
    "littlefs lfs_t ABI changed"
);
_Static_assert(
    __builtin_offsetof(
        struct open_cfw_littlefs_alloc_lookahead_lfs,
        lookahead
    ) == 0x54U,
    "littlefs lookahead offset changed"
);
_Static_assert(
    __builtin_offsetof(
        struct open_cfw_littlefs_alloc_lookahead_lfs,
        lookahead
    ) +
        __builtin_offsetof(
            struct open_cfw_littlefs_alloc_lookahead_state,
            start
        ) == 0x54U,
    "littlefs lookahead start offset changed"
);
_Static_assert(
    __builtin_offsetof(
        struct open_cfw_littlefs_alloc_lookahead_lfs,
        lookahead
    ) +
        __builtin_offsetof(
            struct open_cfw_littlefs_alloc_lookahead_state,
            size
        ) == 0x58U,
    "littlefs lookahead size offset changed"
);
_Static_assert(
    __builtin_offsetof(
        struct open_cfw_littlefs_alloc_lookahead_lfs,
        lookahead
    ) +
        __builtin_offsetof(
            struct open_cfw_littlefs_alloc_lookahead_state,
            buffer
        ) == 0x64U,
    "littlefs lookahead buffer offset changed"
);
_Static_assert(
    __builtin_offsetof(
        struct open_cfw_littlefs_alloc_lookahead_lfs,
        block_count
    ) == 0x6CU,
    "littlefs block-count offset changed"
);
#endif

__attribute__((used, noinline))
int open_cfw_littlefs_alloc_lookahead(
    void *p,
    open_cfw_littlefs_alloc_lookahead_u32 block
)
{
    struct open_cfw_littlefs_alloc_lookahead_lfs *lfs =
        (struct open_cfw_littlefs_alloc_lookahead_lfs *)p;
    open_cfw_littlefs_alloc_lookahead_u32 off =
        ((block - lfs->lookahead.start) + lfs->block_count) %
        lfs->block_count;

    if (off < lfs->lookahead.size) {
        lfs->lookahead.buffer[off / 8U] |=
            (open_cfw_littlefs_alloc_lookahead_u8)(1U << (off % 8U));
    }

    return 0;
}
