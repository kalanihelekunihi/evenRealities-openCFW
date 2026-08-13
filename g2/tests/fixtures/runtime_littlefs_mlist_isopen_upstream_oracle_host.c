/*
 * SPDX-License-Identifier: BSD-3-Clause
 *
 * Host wrapper compiling pristine littlefs v2.10.1 lfs.c as the independent
 * oracle for the isolated lfs_mlist_isopen candidate.
 */

#include <stddef.h>
#include <stdint.h>

#include "../../third_party/littlefs/lfs.c"
#include "../../third_party/littlefs/lfs_util.c"

uint32_t open_cfw_oracle_littlefs_mlist_isopen_call(
    struct lfs_mlist *head,
    struct lfs_mlist *node
)
{
    return lfs_mlist_isopen(head, node) ? 1U : 0U;
}

size_t open_cfw_oracle_littlefs_mlist_isopen_next_offset(void)
{
    return offsetof(struct lfs_mlist, next);
}
