/*
 * SPDX-License-Identifier: BSD-3-Clause
 *
 * Host harness for the isolated littlefs utility-cluster candidate.
 */

#include <stddef.h>
#include <stdint.h>

#include "../../research/candidates/littlefs_util_cluster.c"

static uint32_t open_cfw_test_littlefs_disk_version = 0x00020001U;

uint32_t open_cfw_littlefs_disk_version(
    struct open_cfw_littlefs_disk_version_lfs *lfs
)
{
    (void)lfs;
    return open_cfw_test_littlefs_disk_version;
}

uint32_t open_cfw_test_littlefs_util_max(uint32_t a, uint32_t b)
{
    return open_cfw_littlefs_util_max(a, b);
}

uint32_t open_cfw_test_littlefs_util_min(uint32_t a, uint32_t b)
{
    return open_cfw_littlefs_util_min(a, b);
}

uint32_t open_cfw_test_littlefs_util_aligndown(
    uint32_t a,
    uint32_t alignment
)
{
    return open_cfw_littlefs_util_aligndown(a, alignment);
}

uint32_t open_cfw_test_littlefs_util_alignup(
    uint32_t a,
    uint32_t alignment
)
{
    return open_cfw_littlefs_util_alignup(a, alignment);
}

uint32_t open_cfw_test_littlefs_util_npw2(uint32_t a)
{
    return open_cfw_littlefs_util_npw2(a);
}

uint32_t open_cfw_test_littlefs_util_ctz(uint32_t a)
{
    return open_cfw_littlefs_util_ctz(a);
}

uint32_t open_cfw_test_littlefs_util_popc(uint32_t a)
{
    return open_cfw_littlefs_util_popc(a);
}

uint32_t open_cfw_test_littlefs_util_fromle32(uint32_t a)
{
    return open_cfw_littlefs_util_fromle32(a);
}

uint32_t open_cfw_test_littlefs_util_tole32(uint32_t a)
{
    return open_cfw_littlefs_util_tole32(a);
}

uint32_t open_cfw_test_littlefs_util_frombe32(uint32_t a)
{
    return open_cfw_littlefs_util_frombe32(a);
}

uint32_t open_cfw_test_littlefs_util_tobe32(uint32_t a)
{
    return open_cfw_littlefs_util_tobe32(a);
}

void open_cfw_test_littlefs_util_set_disk_version(uint32_t version)
{
    open_cfw_test_littlefs_disk_version = version;
}

uint16_t open_cfw_test_littlefs_util_disk_version_major(void)
{
    return open_cfw_littlefs_disk_version_major(
        (struct open_cfw_littlefs_disk_version_lfs *)0
    );
}

uint16_t open_cfw_test_littlefs_util_disk_version_minor(void)
{
    return open_cfw_littlefs_disk_version_minor(
        (struct open_cfw_littlefs_disk_version_lfs *)0
    );
}

size_t open_cfw_test_littlefs_util_uint8_size(void)
{
    return sizeof(open_cfw_littlefs_util_u8);
}

size_t open_cfw_test_littlefs_util_uint16_size(void)
{
    return sizeof(open_cfw_littlefs_util_u16);
}

size_t open_cfw_test_littlefs_util_uint32_size(void)
{
    return sizeof(open_cfw_littlefs_util_u32);
}
