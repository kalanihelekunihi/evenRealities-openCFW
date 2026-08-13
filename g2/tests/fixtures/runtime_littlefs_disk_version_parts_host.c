#include <stdint.h>

#include "../../components/apollo_main/core_overlay/runtime_littlefs_disk_version_parts.c"

static uint32_t open_cfw_test_disk_version;
static unsigned open_cfw_test_provider_calls;
static struct open_cfw_littlefs_disk_version_lfs *open_cfw_test_last_lfs;
static struct open_cfw_littlefs_disk_version_lfs *const open_cfw_test_lfs =
    (struct open_cfw_littlefs_disk_version_lfs *)(uintptr_t)0x1234U;

open_cfw_littlefs_disk_version_u32 open_cfw_littlefs_disk_version(
    struct open_cfw_littlefs_disk_version_lfs *lfs
)
{
    open_cfw_test_provider_calls += 1U;
    open_cfw_test_last_lfs = lfs;
    return open_cfw_test_disk_version;
}

void open_cfw_test_littlefs_disk_version_parts_set(uint32_t disk_version)
{
    open_cfw_test_disk_version = disk_version;
    open_cfw_test_provider_calls = 0U;
    open_cfw_test_last_lfs = (void *)0;
}

uint16_t open_cfw_test_littlefs_disk_version_parts_major(void)
{
    return open_cfw_littlefs_disk_version_major(open_cfw_test_lfs);
}

uint16_t open_cfw_test_littlefs_disk_version_parts_minor(void)
{
    return open_cfw_littlefs_disk_version_minor(open_cfw_test_lfs);
}

uint16_t open_cfw_oracle_littlefs_disk_version_parts_major(void)
{
    return (uint16_t)(0xffffU & (open_cfw_test_disk_version >> 16));
}

uint16_t open_cfw_oracle_littlefs_disk_version_parts_minor(void)
{
    return (uint16_t)(0xffffU & (open_cfw_test_disk_version >> 0));
}

unsigned open_cfw_test_littlefs_disk_version_parts_provider_calls(void)
{
    return open_cfw_test_provider_calls;
}

unsigned open_cfw_test_littlefs_disk_version_parts_lfs_forwarded(void)
{
    return open_cfw_test_last_lfs == open_cfw_test_lfs;
}
