/*
 * The little filesystem
 *
 * Copyright (c) 2022, The littlefs authors.
 * Copyright (c) 2017, Arm Limited. All rights reserved.
 * SPDX-License-Identifier: BSD-3-Clause
 *
 * Integrated, freestanding source replacement for lfs_mlist_isopen() from
 * littlefs v2.10.1 lfs.c at commit
 * 0494ce7169f06a734a7bd7585f49a9fa91fa7318, tree
 * 06dd0162169d3cb550cd24a3e34d0e4d02983ad3.
 *
 * Both official G2 images retain the same complete private leaf at
 * Apollo-main [0x004CB082, 0x004CB0A0) and bootloader
 * [0x00410D8A, 0x00410DA8). It is retained by the assertions-enabled
 * configuration in both images. There are no calls, literals, relocations,
 * configuration reads, block callbacks, or MSPI dependencies.
 */

typedef unsigned int open_cfw_littlefs_mlist_isopen_bool;

struct open_cfw_littlefs_mlist_isopen_node {
    struct open_cfw_littlefs_mlist_isopen_node *next;
};

#if defined(__arm__)
_Static_assert(sizeof(void *) == 4U, "Apollo510 requires 32-bit pointers");
_Static_assert(
    sizeof(open_cfw_littlefs_mlist_isopen_bool) == 4U,
    "littlefs G2 bool return ABI changed"
);
_Static_assert(
    __builtin_offsetof(
        struct open_cfw_littlefs_mlist_isopen_node,
        next
    ) == 0U,
    "littlefs mlist next offset changed"
);
#endif

__attribute__((used, noinline))
open_cfw_littlefs_mlist_isopen_bool open_cfw_littlefs_mlist_isopen(
    struct open_cfw_littlefs_mlist_isopen_node *head,
    struct open_cfw_littlefs_mlist_isopen_node *node
)
{
    /*
     * Keep the recovered G2 32-bit 0/1 return ABI. Using C _Bool here makes
     * Clang add canonicalization instructions and changes both reviewed
     * production bodies.
     */
    while (head) {
        if (head == node) {
            return 1U;
        }
        head = head->next;
    }

    return 0U;
}
