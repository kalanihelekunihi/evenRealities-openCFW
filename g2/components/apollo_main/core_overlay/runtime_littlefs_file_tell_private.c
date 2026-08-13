/*
 * The little filesystem
 *
 * Copyright (c) 2022, The littlefs authors.
 * Copyright (c) 2017, Arm Limited. All rights reserved.
 * SPDX-License-Identifier: BSD-3-Clause
 *
 * Bounded, freestanding port of lfs_file_tell_() from littlefs v2.10.1
 * lfs.c at commit 0494ce7169f06a734a7bd7585f49a9fa91fa7318.
 *
 * The official G2 Apollo-main image places this complete private leaf at
 * [0x004CE45C, 0x004CE460). It reads only lfs_file_t.pos at offset 0x34;
 * there are no calls, branches, literals, relocations, configuration reads,
 * allocator operations, block callbacks, or MSPI dependencies.
 */

typedef unsigned int open_cfw_littlefs_file_tell_private_u32;
typedef signed int open_cfw_littlefs_file_tell_private_s32;
typedef unsigned short open_cfw_littlefs_file_tell_private_u16;
typedef unsigned char open_cfw_littlefs_file_tell_private_u8;

struct open_cfw_littlefs_file_tell_private_cache {
    open_cfw_littlefs_file_tell_private_u32 block;
    open_cfw_littlefs_file_tell_private_u32 offset;
    open_cfw_littlefs_file_tell_private_u32 size;
    open_cfw_littlefs_file_tell_private_u8 *buffer;
};

struct open_cfw_littlefs_file_tell_private_mdir {
    open_cfw_littlefs_file_tell_private_u32 pair[2];
    open_cfw_littlefs_file_tell_private_u32 revision;
    open_cfw_littlefs_file_tell_private_u32 offset;
    open_cfw_littlefs_file_tell_private_u32 etag;
    open_cfw_littlefs_file_tell_private_u16 count;
    _Bool erased;
    _Bool split;
    open_cfw_littlefs_file_tell_private_u32 tail[2];
};

struct open_cfw_littlefs_file_tell_private_file {
    struct open_cfw_littlefs_file_tell_private_file *next;
    open_cfw_littlefs_file_tell_private_u16 id;
    open_cfw_littlefs_file_tell_private_u8 type;
    struct open_cfw_littlefs_file_tell_private_mdir directory;

    struct {
        open_cfw_littlefs_file_tell_private_u32 head;
        open_cfw_littlefs_file_tell_private_u32 size;
    } ctz;

    open_cfw_littlefs_file_tell_private_u32 flags;
    open_cfw_littlefs_file_tell_private_u32 position;
    open_cfw_littlefs_file_tell_private_u32 block;
    open_cfw_littlefs_file_tell_private_u32 offset;
    struct open_cfw_littlefs_file_tell_private_cache cache;
    const void *configuration;
};

struct open_cfw_littlefs_file_tell_private_lfs;

#if defined(__arm__)
_Static_assert(sizeof(void *) == 4U, "Apollo510 requires 32-bit pointers");
_Static_assert(
    sizeof(open_cfw_littlefs_file_tell_private_u32) == 4U,
    "littlefs lfs_off_t width changed"
);
_Static_assert(
    sizeof(open_cfw_littlefs_file_tell_private_s32) == 4U,
    "littlefs lfs_soff_t width changed"
);
_Static_assert(
    sizeof(struct open_cfw_littlefs_file_tell_private_mdir) == 0x20U,
    "littlefs lfs_mdir_t ABI changed"
);
_Static_assert(
    sizeof(struct open_cfw_littlefs_file_tell_private_cache) == 0x10U,
    "littlefs lfs_cache_t ABI changed"
);
_Static_assert(
    sizeof(struct open_cfw_littlefs_file_tell_private_file) == 0x54U,
    "littlefs lfs_file_t ABI changed"
);
_Static_assert(
    __builtin_offsetof(
        struct open_cfw_littlefs_file_tell_private_file,
        position
    ) == 0x34U,
    "littlefs lfs_file_t position offset changed"
);
#endif

__attribute__((used, noinline))
open_cfw_littlefs_file_tell_private_s32
open_cfw_littlefs_file_tell_private(
    struct open_cfw_littlefs_file_tell_private_lfs *lfs,
    struct open_cfw_littlefs_file_tell_private_file *file
)
{
    (void)lfs;
    return file->position;
}
