/* SPDX-License-Identifier: MIT
 * Candidate freestanding profile, not recovered stock compiler options.
 * Source allocation stays at the explicit stock allocator/mutex boundary.
 */
#include <stdint.h>
void *opencfw_boot_fs_alloc(uint32_t);
void opencfw_boot_fs_free(void *);
#define LFS_MALLOC(size) opencfw_boot_fs_alloc((uint32_t)(size))
#define LFS_FREE(pointer) opencfw_boot_fs_free(pointer)
