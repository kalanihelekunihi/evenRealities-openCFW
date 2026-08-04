/*
 * SPDX-License-Identifier: BSD-3-Clause
 *
 * Isolated G2 ABI for littlefs v2.10.1 lfs_file_size_(). The private file
 * layout is intentionally reproduced here so this source boundary stays
 * freestanding and does not inherit unrelated littlefs configuration.
 */

#ifndef OPEN_CFW_RUNTIME_LITTLEFS_FILE_SIZE_PRIVATE_H
#define OPEN_CFW_RUNTIME_LITTLEFS_FILE_SIZE_PRIVATE_H

typedef __UINT32_TYPE__ open_cfw_littlefs_file_size_private_u32;
typedef __INT32_TYPE__ open_cfw_littlefs_file_size_private_s32;
typedef __UINT16_TYPE__ open_cfw_littlefs_file_size_private_u16;
typedef __UINT8_TYPE__ open_cfw_littlefs_file_size_private_u8;

struct open_cfw_littlefs_file_size_private_cache {
    open_cfw_littlefs_file_size_private_u32 block;
    open_cfw_littlefs_file_size_private_u32 offset;
    open_cfw_littlefs_file_size_private_u32 size;
    open_cfw_littlefs_file_size_private_u8 *buffer;
};

struct open_cfw_littlefs_file_size_private_mdir {
    open_cfw_littlefs_file_size_private_u32 pair[2];
    open_cfw_littlefs_file_size_private_u32 revision;
    open_cfw_littlefs_file_size_private_u32 offset;
    open_cfw_littlefs_file_size_private_u32 etag;
    open_cfw_littlefs_file_size_private_u16 count;
    _Bool erased;
    _Bool split;
    open_cfw_littlefs_file_size_private_u32 tail[2];
};

struct open_cfw_littlefs_file_size_private_ctz {
    open_cfw_littlefs_file_size_private_u32 head;
    open_cfw_littlefs_file_size_private_u32 size;
};

struct open_cfw_littlefs_file_size_private_file {
    struct open_cfw_littlefs_file_size_private_file *next;
    open_cfw_littlefs_file_size_private_u16 id;
    open_cfw_littlefs_file_size_private_u8 type;
    struct open_cfw_littlefs_file_size_private_mdir directory;
    struct open_cfw_littlefs_file_size_private_ctz ctz;
    open_cfw_littlefs_file_size_private_u32 flags;
    open_cfw_littlefs_file_size_private_u32 position;
    open_cfw_littlefs_file_size_private_u32 block;
    open_cfw_littlefs_file_size_private_u32 offset;
    struct open_cfw_littlefs_file_size_private_cache cache;
    const void *configuration;
};

struct open_cfw_littlefs_file_size_private_lfs;

enum {
    OPEN_CFW_LITTLEFS_FILE_SIZE_PRIVATE_WRITING = 0x00020000U,
    OPEN_CFW_LITTLEFS_FILE_SIZE_PRIVATE_MAX_ADDRESS = 0x004CA6F8U
};

_Static_assert(
    sizeof(open_cfw_littlefs_file_size_private_u32) == 4U,
    "littlefs lfs_size_t width changed"
);
_Static_assert(
    sizeof(open_cfw_littlefs_file_size_private_s32) == 4U,
    "littlefs lfs_soff_t width changed"
);
_Static_assert(
    sizeof(struct open_cfw_littlefs_file_size_private_mdir) == 0x20U,
    "littlefs lfs_mdir_t ABI changed"
);
_Static_assert(
    sizeof(struct open_cfw_littlefs_file_size_private_ctz) == 0x08U,
    "littlefs lfs_ctz ABI changed"
);

#if defined(__arm__)
_Static_assert(sizeof(void *) == 4U, "Apollo510 requires 32-bit pointers");
_Static_assert(
    sizeof(struct open_cfw_littlefs_file_size_private_cache) == 0x10U,
    "littlefs lfs_cache_t ABI changed"
);
_Static_assert(
    sizeof(struct open_cfw_littlefs_file_size_private_file) == 0x54U,
    "littlefs lfs_file_t ABI changed"
);
_Static_assert(
    _Alignof(struct open_cfw_littlefs_file_size_private_file) == 4U,
    "littlefs lfs_file_t alignment changed"
);
_Static_assert(
    __builtin_offsetof(
        struct open_cfw_littlefs_file_size_private_file,
        ctz.size
    ) == 0x2CU,
    "littlefs lfs_file_t ctz.size offset changed"
);
_Static_assert(
    __builtin_offsetof(
        struct open_cfw_littlefs_file_size_private_file,
        flags
    ) == 0x30U,
    "littlefs lfs_file_t flags offset changed"
);
_Static_assert(
    __builtin_offsetof(
        struct open_cfw_littlefs_file_size_private_file,
        position
    ) == 0x34U,
    "littlefs lfs_file_t position offset changed"
);
#endif

/* Source-owned replacement for littlefs lfs_max at stock entry 0x004CA6F8. */
open_cfw_littlefs_file_size_private_u32 open_cfw_littlefs_util_max(
    open_cfw_littlefs_file_size_private_u32 a,
    open_cfw_littlefs_file_size_private_u32 b
);

open_cfw_littlefs_file_size_private_s32
open_cfw_littlefs_file_size_private(
    struct open_cfw_littlefs_file_size_private_lfs *lfs,
    struct open_cfw_littlefs_file_size_private_file *file
);

#endif
