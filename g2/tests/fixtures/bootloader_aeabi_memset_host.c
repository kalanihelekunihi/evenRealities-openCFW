#include <stddef.h>

#include "../../components/bootloader/core_overlay/runtime_aeabi_memset.c"

void open_cfw_bootloader_memset_fixture(
    unsigned char *destination,
    size_t count,
    int value
)
{
    open_cfw_bootloader_aeabi_memset(destination, count, value);
}
