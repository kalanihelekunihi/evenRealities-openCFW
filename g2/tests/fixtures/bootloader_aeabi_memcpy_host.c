#include "../../components/bootloader/core_overlay/runtime_aeabi_memcpy.c"

void open_cfw_bootloader_memcpy_fixture(
    unsigned char *destination,
    const unsigned char *source,
    open_cfw_bootloader_memcpy_size count
)
{
    open_cfw_bootloader_aeabi_memcpy(destination, source, count);
}
