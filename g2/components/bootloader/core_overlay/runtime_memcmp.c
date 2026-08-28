/* SPDX-License-Identifier: MIT */

#include "runtime_memcmp.h"

__attribute__((used, noinline))
int open_cfw_bootloader_memcmp(
    const void *left,
    const void *right,
    open_cfw_bootloader_memcmp_size count
)
{
    const unsigned char *lhs = (const unsigned char *)left;
    const unsigned char *rhs = (const unsigned char *)right;

    while (count != 0U) {
        if (*lhs != *rhs) {
            return (int)*lhs - (int)*rhs;
        }
        ++lhs;
        ++rhs;
        --count;
    }
    return 0;
}
