/* SPDX-License-Identifier: MIT
 * Stock internal unmount entry: deinitialise the littlefs instance. */
#include <stdint.h>

struct lfs;
extern int opencfw_boot_lfs_deinit_4144dc(struct lfs *lfs);

int opencfw_boot_lfs_unmount_internal_abi(struct lfs *lfs)
{
    return opencfw_boot_lfs_deinit_4144dc(lfs);
}
