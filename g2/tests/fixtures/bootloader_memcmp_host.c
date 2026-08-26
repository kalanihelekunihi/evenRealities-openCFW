#include "../../components/bootloader/core_overlay/runtime_memcmp.c"

int open_cfw_bootloader_memcmp_fixture(
    const unsigned char *left,
    const unsigned char *right,
    open_cfw_bootloader_memcmp_size count
)
{
    return open_cfw_bootloader_memcmp(left, right, count);
}
