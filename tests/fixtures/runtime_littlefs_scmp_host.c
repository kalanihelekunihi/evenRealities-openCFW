/*
 * SPDX-License-Identifier: BSD-3-Clause
 *
 * Host harness for the source-owned littlefs lfs_scmp boundary.
 */

#include <stddef.h>
#include <stdint.h>

#include \
    "../../components/apollo_main/core_overlay/runtime_littlefs_scmp.c"

int32_t open_cfw_test_littlefs_scmp_call(uint32_t a, uint32_t b)
{
    return open_cfw_littlefs_scmp(a, b);
}

size_t open_cfw_test_littlefs_scmp_uint32_size(void)
{
    return sizeof(open_cfw_littlefs_scmp_u32);
}

size_t open_cfw_test_littlefs_scmp_unsigned_size(void)
{
    return sizeof(unsigned);
}

size_t open_cfw_test_littlefs_scmp_int_size(void)
{
    return sizeof(int);
}
