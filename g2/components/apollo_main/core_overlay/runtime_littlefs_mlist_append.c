/*
 * The little filesystem
 *
 * Copyright (c) 2022, The littlefs authors.
 * Copyright (c) 2017, Arm Limited. All rights reserved.
 * SPDX-License-Identifier: BSD-3-Clause
 *
 * Integrated, freestanding source replacement for lfs_mlist_append() from
 * littlefs v2.10.1 lfs.c at commit
 * 0494ce7169f06a734a7bd7585f49a9fa91fa7318.
 *
 * Both official G2 images retain the same complete private leaf at
 * Apollo-main [0x004CB0BC, 0x004CB0C4) and bootloader
 * [0x00410DC4, 0x00410DCC). It links the node to the old lfs_t.mlist head,
 * then publishes the node as the new head. There are no calls, literals,
 * relocations, configuration reads, block callbacks, or MSPI dependencies.
 */

typedef unsigned char open_cfw_littlefs_mlist_append_u8;
typedef unsigned short open_cfw_littlefs_mlist_append_u16;
typedef unsigned int open_cfw_littlefs_mlist_append_u32;

struct open_cfw_littlefs_mlist_append_node {
    struct open_cfw_littlefs_mlist_append_node *next;
    open_cfw_littlefs_mlist_append_u16 id;
    open_cfw_littlefs_mlist_append_u8 type;
};

struct open_cfw_littlefs_mlist_append_cache {
    open_cfw_littlefs_mlist_append_u32 block;
    open_cfw_littlefs_mlist_append_u32 offset;
    open_cfw_littlefs_mlist_append_u32 size;
    open_cfw_littlefs_mlist_append_u8 *buffer;
};

struct open_cfw_littlefs_mlist_append_gstate {
    open_cfw_littlefs_mlist_append_u32 tag;
    open_cfw_littlefs_mlist_append_u32 pair[2];
};

struct open_cfw_littlefs_mlist_append_config;

struct open_cfw_littlefs_mlist_append_lookahead {
    open_cfw_littlefs_mlist_append_u32 start;
    open_cfw_littlefs_mlist_append_u32 size;
    open_cfw_littlefs_mlist_append_u32 next;
    open_cfw_littlefs_mlist_append_u32 checkpoint;
    open_cfw_littlefs_mlist_append_u8 *buffer;
};

struct open_cfw_littlefs_mlist_append_lfs {
    struct open_cfw_littlefs_mlist_append_cache read_cache;
    struct open_cfw_littlefs_mlist_append_cache program_cache;

    open_cfw_littlefs_mlist_append_u32 root[2];
    struct open_cfw_littlefs_mlist_append_node *open_list;
    open_cfw_littlefs_mlist_append_u32 seed;

    struct open_cfw_littlefs_mlist_append_gstate global_state;
    struct open_cfw_littlefs_mlist_append_gstate disk_state;
    struct open_cfw_littlefs_mlist_append_gstate delta_state;

    struct open_cfw_littlefs_mlist_append_lookahead lookahead;

    const struct open_cfw_littlefs_mlist_append_config *configuration;
    open_cfw_littlefs_mlist_append_u32 block_count;
    open_cfw_littlefs_mlist_append_u32 name_max;
    open_cfw_littlefs_mlist_append_u32 file_max;
    open_cfw_littlefs_mlist_append_u32 attribute_max;
    open_cfw_littlefs_mlist_append_u32 inline_max;
};

#if defined(__arm__)
_Static_assert(sizeof(void *) == 4U, "Apollo510 requires 32-bit pointers");
_Static_assert(
    sizeof(open_cfw_littlefs_mlist_append_u32) == 4U,
    "littlefs 32-bit scalar width changed"
);
_Static_assert(
    sizeof(struct open_cfw_littlefs_mlist_append_cache) == 0x10U,
    "littlefs lfs_cache_t ABI changed"
);
_Static_assert(
    sizeof(struct open_cfw_littlefs_mlist_append_gstate) == 0x0CU,
    "littlefs lfs_gstate_t ABI changed"
);
_Static_assert(
    sizeof(struct open_cfw_littlefs_mlist_append_lookahead) == 0x14U,
    "littlefs lfs_lookahead ABI changed"
);
_Static_assert(
    sizeof(struct open_cfw_littlefs_mlist_append_lfs) == 0x80U,
    "littlefs lfs_t ABI changed"
);
_Static_assert(
    __builtin_offsetof(
        struct open_cfw_littlefs_mlist_append_lfs,
        open_list
    ) == 0x28U,
    "littlefs lfs_t mlist offset changed"
);
_Static_assert(
    __builtin_offsetof(
        struct open_cfw_littlefs_mlist_append_node,
        next
    ) == 0U,
    "littlefs mlist next offset changed"
);
_Static_assert(
    __builtin_offsetof(
        struct open_cfw_littlefs_mlist_append_node,
        id
    ) == 4U,
    "littlefs mlist id offset changed"
);
_Static_assert(
    __builtin_offsetof(
        struct open_cfw_littlefs_mlist_append_node,
        type
    ) == 6U,
    "littlefs mlist type offset changed"
);
#endif

__attribute__((used, noinline))
void open_cfw_littlefs_mlist_append(
    struct open_cfw_littlefs_mlist_append_lfs *lfs,
    struct open_cfw_littlefs_mlist_append_node *mlist
)
{
    mlist->next = lfs->open_list;

    /*
     * Preserve upstream's link-before-publish operation at the machine-code
     * boundary. This compiler barrier emits no instruction and introduces no
     * dependency.
     */
    __asm__ volatile("" ::: "memory");

    lfs->open_list = mlist;
}
